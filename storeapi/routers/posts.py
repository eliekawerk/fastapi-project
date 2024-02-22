import logging

from fastapi import APIRouter, HTTPException

from storeapi.database import comments_table, database, post_table
from storeapi.models.post import (
    Comment,
    CommentIn,
    UserPost,
    UserPostIn,
    UserPostWithComments,
)

router = APIRouter()
logger = logging.getLogger(__name__)


async def find_post(post_id: int):
    logger.info(f"finding post with post id: {post_id}")
    query = post_table.select().where(post_table.c.id == post_id)
    return await database.fetch_one(query)


@router.post("/post", response_model=UserPost, status_code=201)
async def create_post(post: UserPostIn):
    data = post.model_dump()
    query = post_table.insert().values(data)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}


@router.get("/post", response_model=list[UserPost])
async def get_all_posts():
    logger.info("Getting all posts")
    query = post_table.select()
    logger.debug(query)
    return await database.fetch_all(query)


@router.post("/comment", response_model=Comment, status_code=201)
async def create_comment(comment: CommentIn):
    post = await find_post(comment.post_id)
    if not post:
        logger.error(f"Post with id: {comment.post_id} not found")
        raise HTTPException(status_code=404, detail="Post not found")
    data = comment.model_dump()
    query = comments_table.insert(values=data)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}


@router.get("/post/{post_id}/comment", response_model=list[Comment])
async def get_comments_on_post(post_id: int):
    logger.info(f"Getting comments on post id: {post_id}")
    query = comments_table.select().where(comments_table.c.post_id == post_id)
    logger.debug(query, extra={"email": "bob@example.com"})
    return await database.fetch_all(query)


@router.get("/post/{post_id}", response_model=UserPostWithComments)
async def get_post_with_comments(post_id: int):
    logger.info("Get post with its comments")
    post = await find_post(post_id)
    if not post:
        logger.info(f"post with post id: {post_id} not found")
        raise HTTPException(status_code=404, detail="Post not found")
    return {"post": post, "comments": await get_comments_on_post(post_id)}
