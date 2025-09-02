# API Example Usage (curl)

## 1. Get Posts (Infinite Scroll)
```sh
curl --location 'http://127.0.0.1:8000/api/posts/'
```

## 2. Register User
```sh
curl --location 'http://127.0.0.1:8000/register/' \
--header 'Content-Type: application/json' \
--data-raw '{
    "username": "sanjay",
    "email": "sanjay@example.com",
    "password": "mypassword"
}'
```

## 3. Login
```sh
curl --location 'http://127.0.0.1:8000/api/login/' \
--header 'Content-Type: application/json' \
--data '{
    "username": "sanjay",
    "password": "mypassword"
}'
```

## 4. Create Post (Authenticated)
```sh
curl --location 'http://127.0.0.1:8000/api/posts/create/' \
--header 'Content-Type: application/json' \
--header 'Authorization: Basic c2FuamF5Om15cGFzc3dvcmQ=' \
--data '{
    "text": "text for Post"
}'
```

## 5. Add Comment to Post (Authenticated)
```sh
curl --location 'http://127.0.0.1:8000/api/comments/add/' \
--header 'Content-Type: application/json' \
--header 'Authorization: Basic c2FuamF5Om15cGFzc3dvcmQ=' \
--data '{
    "post_id": "aa36d1ec-a1ae-428b-a857-599e9c1fd1a0",
    "text": "Text for comment"
}'
```
