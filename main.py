from fastapi import FastAPI, Request
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from parser import parseAnime
from db_actions import get_anime_list, insert_anime, delete_anime_by_name, check_anime, update_anime
from PIL import Image
from io import BytesIO
import json
from fastapi import FastAPI

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:5173",
    "http://192.168.31.140:5173",
    "http://37.110.44.172:65"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.post("/new_anime")
async def root(request: Request):
    data = await request.json()
    info = parseAnime(URL=data['url'])
    insert_anime(info['name'], info['url'], info['episodes'], info['release'], info['image'],
                 ', '.join(['{0}'.format(x) for x in info['genre_list']]),
                 ', '.join(['{0}'.format(x) for x in info['voice_over']]), info['next_episodes'])
    info['genre_list'] = ', '.join(['{0}'.format(x) for x in info['genre_list']])
    info['voice_over'] = ', '.join(['{0}'.format(x) for x in info['voice_over']])
    return json.dumps(info, ensure_ascii=False)


@app.post("/update_anime")
async def root(request: Request):
    data = await request.json()
    info = parseAnime(URL=data['url'])
    update_anime(info['name'], info['url'], info['episodes'], info['release'], info['image'],
                 ', '.join(['{0}'.format(x) for x in info['genre_list']]),
                 ', '.join(['{0}'.format(x) for x in info['voice_over']]), info['next_episodes'])
    info['genre_list'] = ', '.join(['{0}'.format(x) for x in info['genre_list']])
    info['voice_over'] = ', '.join(['{0}'.format(x) for x in info['voice_over']])
    return json.dumps(info, ensure_ascii=False)


@app.get("/anime_list")
async def root():
    info = get_anime_list()
    print(info)
    return info


@app.post("/update_all")
async def updateAnimeData():
    print('update_all')


@app.get("/images/{image_name}")
async def read_image(image_name: str):
    with open(f"ani_images/{image_name}.jpg", "rb") as f:
        image_data = f.read()
    return Response(content=image_data, media_type="image/jpeg")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
