from concurrent import futures
import datetime
import grpc
import posts_service_pb2, posts_service_pb2_grpc
from db import SessionLocal
import models


class PostService(posts_service_pb2_grpc.PostService):
    def CreatePost(self, request, context):
        db = SessionLocal()
        now = datetime.datetime.now()
        entity = models.Post(
            users_id=request.userId,
            author=request.userLogin,
            title=request.title,
            text=request.text,
            creation_date=now
        )

        db.add(entity)
        db.commit()
        db.refresh(entity)

        post_info = posts_service_pb2.PostInfo(
            id=entity.id,
            author=request.userLogin,
            title=entity.title,
            text=entity.text,
            creationDate=int(now.strftime('%s'))
        )

        db.close()
        return posts_service_pb2.PostInfoOrErrorReply(
            isOk=True,
            postInfo=post_info
        )

    def UpdatePost(self, request, context):
        db = SessionLocal()
        query = db.query(models.Post).filter((models.Post.id == request.postId))
        if query.first() is None:
            db.close()
            return posts_service_pb2.PostInfoOrErrorReply(
                isOk=False,
                errorCode=404,
                errorText='post not found'
            )

        post = query.first()
        if post.users_id != request.userId:
            db.close()
            return posts_service_pb2.PostInfoOrErrorReply(
                isOk=False,
                errorCode=403,
                errorText='permission denied'
            )

        query.update({
            'title': request.title,
            'text': request.text
        })
        db.commit()

        post_info = posts_service_pb2.PostInfo(
            id=post.id,
            author=request.userLogin,
            title=request.title,
            text=request.text,
            creationDate=int(post.creation_date.strftime('%s'))
        )

        db.close()
        return posts_service_pb2.PostInfoOrErrorReply(
            isOk=True,
            postInfo=post_info
        )

    def DeletePost(self, request, context):
        db = SessionLocal()
        query = db.query(models.Post).filter((models.Post.id == request.postId))
        if query.first() is None:
            db.close()
            return posts_service_pb2.OkOrErrorReply(
                isOk=False,
                errorCode=404,
                errorText='post not found'
            )

        post = query.first()
        if post.users_id != request.userId:
            db.close()
            return posts_service_pb2.OkOrErrorReply(
                isOk=False,
                errorCode=403,
                errorText='permission denied'
            )

        db.delete(post)
        db.commit()
        db.close()
        return posts_service_pb2.OkOrErrorReply(
            isOk=True,
        )

    def GetPost(self, request, context):
        db = SessionLocal()
        query = db.query(models.Post).filter((models.Post.id == request.postId))
        if query.first() is None:
            db.close()
            return posts_service_pb2.PostInfoOrErrorReply(
                isOk=False,
                errorCode=404,
                errorText='post not found'
            )

        post = query.first()

        post_info = posts_service_pb2.PostInfo(
            id=post.id,
            author=post.author,
            title=post.title,
            text=post.text,
            creationDate=int(post.creation_date.strftime('%s'))
        )
        db.close()

        return posts_service_pb2.PostInfoOrErrorReply(
            isOk=True,
            postInfo=post_info
        )

    def GetAllPosts(self, request, context):
        db = SessionLocal()
        query = db.query(models.Post).filter((models.Post.author == request.userLogin))
        if query is None:
            db.close()
            return posts_service_pb2.PostsOrErrorReply(
                isOk=True,
                posts=[]
            )

        posts = query.all()
        start = request.cursorStart
        end = request.cursorEnd

        result = posts_service_pb2.PostsOrErrorReply()
        result.isOk = True
        for post in posts:
            if post.id >= start and post.id < end:
                result.posts.add(
                    id=post.id,
                    author=post.author,
                    title=post.title,
                    text=post.text,
                    creationDate=int(post.creation_date.strftime('%s'))
                )
        db.close()

        return result


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    posts_service_pb2_grpc.add_PostServiceServicer_to_server(PostService(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
