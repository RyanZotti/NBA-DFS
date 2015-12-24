import pymysql
from Optimizer import Optimizer
con = pymysql.connect(host='localhost', unix_socket='/tmp/mysql.sock', user='root', passwd="", db='NBA')
mysql = con.cursor(pymysql.cursors.DictCursor)

playoff_year = 2015
mysql.execute('delete from dfs_backtesting;')
mysql.execute('delete from dfs_avg_preds;')
mysql.execute('''
    insert into dfs_avg_preds
    select 
        b.game_date, a.player_name, pred as DFS_pred,
        a.DFS_target,b.salary,position
    from dfs_avgs as a 
    left join dfs_salaries as b on a.t_date = b.game_date and a.player_name = b.full_name
    left join playerHeightAndPosition as pos on a.playoffyear = pos.playoff_year and a.team = pos.team and a.player_id = pos.player_id
    where position in ('C','SF','PG','PF','SG')
    having game_date is not null and dfs_target is not null and 
        salary is not null and position is not null
''')

optimizer = Optimizer(max_iterations=1000000)

def get_point_threshold(game_date):
    mysql.execute('''
    create temporary table match_count
    select game_date, count(*) as count from matches where game_date = '{game_date}';
    '''.format(game_date=game_date))
    mysql.execute('''
    select average from match_count left join FanDuel_avg_worst_winning_score as worst on match_count.count = worst.games 
    ''')
    avg = 0
    for row in mysql.fetchall():
        avg = row['average']
    mysql.execute('drop table match_count')    
    return avg

mysql.execute('''
    select game_date, count(*) as count from dfs_avg_preds group by game_date
having count > 14
''')
for row in mysql.fetchall():
    game_date = row['game_date']
    try:
        best_node = optimizer.get_best_lineup('dfs_avg_preds',str(game_date))
    except:
        continue
    actual_value = best_node.actual_value
    predicted_value = best_node.value
    point_threshold = get_point_threshold(game_date)
    mysql.execute("""insert into dfs_backtesting(game_date, predicted_value, actual_value, point_threshold) values("{game_date}","{predicted_value}","{actual_value}","{point_threshold}")""".format(game_date=game_date,predicted_value=predicted_value,actual_value=actual_value,point_threshold=point_threshold))
    con.commit()

print('Finished')
# simple average win rate: 0.2244

