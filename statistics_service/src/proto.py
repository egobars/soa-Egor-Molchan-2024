from concurrent import futures
from grpc import aio                                                            
import statistics_service_pb2, statistics_service_pb2_grpc
import clickhouse_connect

client = clickhouse_connect.get_client(host='snet-clickhouse')

class StatsService(statistics_service_pb2_grpc.StatsService):
    def GetPostStats(self, request, context):
        likes_query = client.query('SELECT count FROM (SELECT post_id, count() as count FROM (SELECT DISTINCT user_id, post_id FROM snet.posts_stats WHERE type=\'LIKE\') GROUP BY post_id) WHERE post_id=' + str(request.postId)).result_rows
        likes = 0
        if len(likes_query) > 0:
            likes = likes_query[0][0]
        views_query = client.query('SELECT count FROM (SELECT post_id, count() as count FROM (SELECT DISTINCT user_id, post_id FROM snet.posts_stats WHERE type=\'VIEW\') GROUP BY post_id) WHERE post_id=' + str(request.postId)).result_rows
        views = 0
        if len(views_query) > 0:
            views = views_query[0][0]

        post_stats = statistics_service_pb2.PostStats(
            id=request.postId,
            likes=likes,
            views=views,
        )

        '''
        SELECT post_id, count FROM
        (SELECT post_id, count() as count FROM
        (SELECT DISTINCT user_id, post_id FROM snet_statistics.stats WHERE type='LIKE')
        GROUP BY post_id)
        ORDER BY count DESC LIMIT 5
        '''

        return statistics_service_pb2.PostStatsOrErrorReply(
            isOk=True,
            postStats=post_stats
        )

    def GetTopPosts(self, request, context):
        if request.isLikes:
            query = client.query('SELECT post_id, count FROM (SELECT post_id, count() as count FROM (SELECT DISTINCT user_id, post_id FROM snet.posts_stats WHERE type=\'LIKE\') GROUP BY post_id) ORDER BY count DESC LIMIT 5').result_rows
        else:
            query = client.query('SELECT post_id, count FROM (SELECT post_id, count() as count FROM (SELECT DISTINCT user_id, post_id FROM snet.posts_stats WHERE type=\'VIEW\') GROUP BY post_id) ORDER BY count DESC LIMIT 5').result_rows
        
        result = statistics_service_pb2.TopPostsStatsOrErrorReply()
        result.isOk = True
        for row in query:
            result.posts.add(
                id=row[0],
                stat=row[1]
            )

        '''
        SELECT post_id, count FROM
        (SELECT post_id, count() as count FROM
        (SELECT DISTINCT user_id, post_id FROM snet_statistics.stats WHERE type='LIKE')
        GROUP BY post_id)
        ORDER BY count DESC
        LIMIT 5
        '''

        return result
    
    def GetTopUsers(self, request, context):
        query = client.query('SELECT author, count FROM (SELECT author, count() as count FROM (SELECT DISTINCT user_id, post_id, author FROM snet.authors_stats) GROUP BY author) ORDER BY count DESC LIMIT 3').result_rows
        
        result = statistics_service_pb2.TopUsersOrErrorReply()
        result.isOk = True
        for row in query:
            result.users.add(
                login=row[0],
                likes=row[1]
            )

        '''
        SELECT post_id, count FROM
        (SELECT post_id, count() as count FROM
        (SELECT DISTINCT user_id, post_id FROM snet_statistics.stats WHERE type='LIKE')
        GROUP BY post_id)
        ORDER BY count DESC
        LIMIT 5
        '''

        return result

async def serve():
    server = aio.server(futures.ThreadPoolExecutor(max_workers=2))
    statistics_service_pb2_grpc.add_StatsServiceServicer_to_server(StatsService(), server)
    server.add_insecure_port("[::]:50051")
    await server.start()
    await server.wait_for_termination()
