import pymysql
from pandas import DataFrame
import numpy as np
import operator
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import ElasticNet

con = pymysql.connect(host='localhost', unix_socket='/tmp/mysql.sock', user='root', passwd="", db='NBA')
mysql = con.cursor(pymysql.cursors.DictCursor)
model_types = {'GBM':GradientBoostingRegressor(),
               'ElasticNet':ElasticNet()}

def get_teams(playoff_year):
    mysql.execute('''
        select home as team from matches where playoffyear = {playoff_year} group by team asc
    '''.format(playoff_year=playoff_year))
    teams = []
    for row in mysql.fetchall():
        teams.append(row['team'])
    return teams

def get_team_game_dates(playoff_year,team):
    minimum_games = 10
    mysql.execute('set @rownum := 0;')
    mysql.execute(''' 
        select game_date from (
            select game_date, @rownum := @rownum + 1 As rank
            from matches 
            where (home = '{team}' or away = '{team}') and 
            playoffyear = {playoff_year} order by game_date asc) as tbl 
        where rank >= {minimum_games}
    '''.format(team=team,playoff_year=playoff_year,minimum_games=minimum_games))
    dates = []
    for row in mysql.fetchall():
        dates.append(row['game_date'])
    return dates

def get_training_set(team,target_date,playoff_year):
    mysql.execute('''
        select a.*,MP_avg_prev, if(vegas_pred < 6.5 and p.starter='starter',1,0) as vegas_line,
            if(p.starter='starter',1,0) as starter_ind from (
            select d.*,
            left(t_players.MP,locate(':',t_players.MP)-1) as MP_target,
            avg(left(prev_players.MP,locate(':',prev_players.MP)-1)) as MP_avg_prev_x_games,
            avg(left(prev_players.MP,locate(':',prev_players.MP)-1)*48/pace.minutes) as MP_avg_prev_x_games_ot_rescaled
            from drivers_players_ranked as d
            left join pace on d.predictor_gameid = pace.game_id
            left join players as prev_players on d.predictor_gameid = prev_players.game_id and d.team = prev_players.team and d.player_id = prev_players.player_id
            left join players as t_players on d.target_gameid = t_players.game_id and d.team = t_players.team and d.player_id = t_players.player_id
            where playoffyear in ({playoff_year}) and time_index < 3 and d.t_date < '{t_date}' and d.team = '{team}'
            group by target_gameid, player_id) as a
        left join DFS_predictors as d on
        a.target_gameid = d.target_gameid and a.team = d.team and a.player_id = d.player_id
        left join players as p on a.target_gameid = p.game_id and a.team = p.team and a.player_id = p.player_id
        left join matches as m on a.target_gameid = m.game_id
        having MP_avg_prev is not null and MP_avg_prev_x_games is not null and MP_target is not null
    '''.format(team=team,playoff_year=playoff_year,t_date=target_date))
    dataset = DataFrame(mysql.fetchall())
    return dataset

def get_test_set(team,target_date,playoff_year):
    mysql.execute('''
        select a.*,MP_avg_prev, if(vegas_pred < 6.5 and p.starter='starter',1,0) as vegas_line,
        if(p.starter='starter',1,0) as starter_ind from (
            select d.*,
            left(t_players.MP,locate(':',t_players.MP)-1) as MP_target,
            avg(left(prev_players.MP,locate(':',prev_players.MP)-1)) as MP_avg_prev_x_games,
            avg(left(prev_players.MP,locate(':',prev_players.MP)-1)*48/pace.minutes) as MP_avg_prev_x_games_ot_rescaled
            from drivers_players_ranked as d
            left join pace on d.predictor_gameid = pace.game_id
            left join players as prev_players on d.predictor_gameid = prev_players.game_id and d.team = prev_players.team and d.player_id = prev_players.player_id
            left join players as t_players on d.target_gameid = t_players.game_id and d.team = t_players.team and d.player_id = t_players.player_id
            where playoffyear in ({playoff_year}) and time_index < 3 and d.t_date = '{t_date}' and d.team = '{team}'
            group by target_gameid, player_id) as a
        left join DFS_predictors as d on
        a.target_gameid = d.target_gameid and a.team = d.team and a.player_id = d.player_id
        left join players as p on a.target_gameid = p.game_id and a.team = p.team and a.player_id = p.player_id
        left join matches as m on a.target_gameid = m.game_id
        having MP_avg_prev is not null and MP_avg_prev_x_games is not null and MP_target is not null
    '''.format(team=team,playoff_year=playoff_year,t_date=target_date))
    dataset = DataFrame(mysql.fetchall())
    return dataset

def save_predictions(predictions):
    for index, row in predictions.iterrows():
        playoffyear = row['playoffyear']
        target_gameid = row['target_gameid']
        team = row['team']
        mp_avg_prev = row['MP_avg_prev']
        player_id = row['player_id']
        pred = row['predicted_minutes']
        target = row['MP_target']
        mysql.execute("""insert into individualized_minutes_pred(playoffyear, target_gameid, team, player_id, pred, mp_avg_prev, target) values("{playoffyear}","{target_gameid}","{team}","{player_id}","{pred}","{mp_avg_prev}","{target}")""".format(playoffyear=playoffyear,target_gameid=target_gameid,team=team,player_id=player_id,pred=pred,mp_avg_prev=mp_avg_prev,target=target))
        con.commit()

def get_best_scores(model_type,predictor_sets,training,validation,team,target_date):
    parameters = []
    if model_type == 'GBM':
        training_record_count = len(training)
        parameters = get_gbm_parameters(training_record_count)
    elif model_type == 'ElasticNet':
        training_record_count = len(training)
        parameters = get_elastic_net_paramaters()
    results = {}
    hashable_results = {}
    for predictor_set in predictor_sets:
        model = GridSearchCV(model_types[model_type], parameters,n_jobs=8)
        model.fit(training[predictor_set], training['MP_target'])
        validation['pred']=model.predict(validation[predictor_set])
        rmse_model = np.sqrt(mean_squared_error(validation['MP_target'], validation['pred']))
        results[str(predictor_set)]=rmse_model
        hashable_results[str(predictor_set)]=predictor_set
    sorted_results = sorted(results.items(), key=operator.itemgetter(1))
    for result in sorted_results:
        best_predictor_set = result[0]
        break
    model.fit(training[hashable_results[best_predictor_set]], training['MP_target'])
    validation['predicted_minutes']=model.predict(validation[hashable_results[best_predictor_set]])
    print(team+" "+str(target_date)+" "+best_predictor_set)
    return validation

def get_elastic_net_paramaters():
    parameters = [{'alpha':np.arange(0.3,1,0.1),'l1_ratio':np.arange(0.1,1,0.1)}]
    return parameters
    
def get_gbm_parameters(training_record_count):
    size_denominator = 5
    max_trees = int((training_record_count - training_record_count%size_denominator)/size_denominator) # 1/10 as a rule of thumb
    min_trees = 5
    range_of_trees = list(range(min_trees,max(min_trees,max_trees)+1,25)) # Looks like 5, 30, 55, 80, etc
    parameters = {'n_estimators':range_of_trees,
                  'learning_rate':[.01,0.1],
                  'max_depth':[1,2,3]}
    return parameters
    
playoff_year = 2003
teams = get_teams(playoff_year)
for team in teams:
    target_dates = get_team_game_dates(playoff_year,team)
    for target_date in target_dates:
        training = get_training_set(team,target_date,playoff_year)
        validation = get_test_set(team,target_date,playoff_year)
        predictor_sets = [
            ['MP_avg_prev'],
            ['MP_avg_prev','MP_avg_prev_x_games'],
            ['MP_avg_prev','MP_avg_prev_x_games','vegas_line'],
            ['MP_avg_prev','MP_avg_prev_x_games','vegas_line','MP_avg_prev_x_games_ot_rescaled'],
            ['MP_avg_prev_x_games_ot_rescaled'],
            ['MP_avg_prev_x_games']
        ]
        #validation=elastic_net(training,validation,predictor_sets)
        #validation=gbm(training,validation,predictor_sets)
        validation=get_best_scores('ElasticNet',predictor_sets,training,validation,team,target_date)
        save_predictions(validation)
print('Finished')
