import csv
import requests
from parsel import Selector

url = "https://maoyan.com/films?showType=3"

headers = {
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'Upgrade-Insecure-Requests': '1',
    'DNT': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
    'Sec-Fetch-User': '?1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Sec-Fetch-Site': 'cross-site',
    'Sec-Fetch-Mode': 'navigate',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Cookie': '_lxsdk_s=172ea7978ed-b2d-cd0-b3d%7C%7C1; uuid_n_v=v1; uuid=BC1C7CD0B6B911EAA1F189776DB49E05C2C094AFA94641F1A97402C984A5DE48; _csrf=d76b9b6f45414a0deb5646eff589ec61bebe0cf0b757ef49242600c3c7af2b17'
}


def get_html():
    response = requests.get(url, headers=headers)
    html = response.text
    return html


def get_movie(html):
    sel = Selector(text=html)
    dd = sel.xpath("//div[@class='movies-list']/dl[@class='movie-list']/dd")
    # html 中 <dd> 没有闭合标签, 使用 Selector 后, 自动补上 </dd>, 但每个 <dd> 标签已不是并列的, 而是层层嵌套
    while True:
        movie_item = dd.xpath("div[contains(@class, 'movie-item')]")
        movie_id = movie_item.xpath("a/@data-val").re_first(r"\d+")
        movie_url = f"https://maoyan.com/films/{movie_id}"
        # poster = movie_item.xpath("a/div[@class='movie-poster']/img[last()]/@data-src").get()  # 160*220
        poster = movie_item.xpath("div[@class='movie-item-hover']/a/img/@src").get()  # 218*300

        name = dd.xpath("div[contains(@class, 'movie-item-title')]/@title").get()
        score = dd.xpath("div[contains(@class, 'channel-detail channel-detail-orange')]//text()").getall()
        score = ''.join(score)

        # 类型, 主演, 上映时间
        info = {}
        for div in movie_item.xpath("div[@class='movie-item-hover']//div[@class='movie-hover-info']/div")[1:]:
            t = div.xpath(".//text()").getall()
            t = [i.strip() for i in t if i and i.strip()]
            t = ''.join(t)
            k, v = t.split(':', 1)
            info.update({k: v})

        movie = {
            '_id': movie_id,
            'name': name,
            'score': score,
            'url': movie_url,
            'poster': poster,
            'info': info,
        }
        yield movie
        dd = dd.xpath('./dd')

        if not dd:
            break


def main():
    html = get_html()
    out_file = 'maoyan_movie_requests.csv'
    with open(out_file, 'w', encoding='GBK') as _f:
        fieldnames = ['_id', 'name', 'score', 'info', 'url', 'poster', ]
        writer = csv.DictWriter(_f, fieldnames=fieldnames, lineterminator='\n')
        writer.writeheader()
        for item in get_movie(html):
            writer.writerow(item)


if __name__ == '__main__':
    main()