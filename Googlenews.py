import pandas as pd
import jieba
from GoogleNews import GoogleNews
from bs4 import BeautifulSoup
import requests
import numpy as np
from PIL import Image
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud, ImageColorGenerator
from scipy.ndimage import gaussian_gradient_magnitude
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

googlenews = GoogleNews()

googlenews.setlang('cn')
googlenews.setperiod('d')
googlenews.setencode('utf-8')
googlenews.clear()

x = input("請輸入要搜尋的關鍵字，將為你搜集相關字詞內容:")
googlenews.search(x)

alldata = googlenews.result()
result = googlenews.gettext()
links = googlenews.get_links()

print()

for n in range(len(result)):
    print(result[n])
    print(links[n])

df = pd.DataFrame(
    {
        '標題': result,
        '連結': links
    })

url = df['連結'][0]

print(url)

user_agent = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}

r = requests.get(url, headers=user_agent)
r.encoding = "utf-8"
web_content = r.text
soup = BeautifulSoup(web_content, 'html.parser')

articleContent = soup.find_all('p')

article = []
for p in articleContent:
    article.append(p.text)

articleAll = '\n'.join(article)

jieba.load_userdict('/Users/zhonghonghao/googlenews-wordCloud/dict.txt.big.txt')

d = articleAll.replace('!', '').replace('／', "").replace('《', '').replace('》', '').replace('，', '').replace('。', '').replace(
    '「', '').replace('」', '').replace('（', '').replace('）', '').replace('！', '').replace('？', '').replace('、',
                                                                                                          '').replace(
    '▲', '').replace('…', '').replace('：', '')


jieba.setLogLevel(10)

Sentence = jieba.cut_for_search(d)

with open('/Users/zhonghonghao/googlenews-wordCloud/stopword.txt', 'r', encoding="utf-8") as f:
    stopwords = f.read().split('\n')

terms = {}
for sentence in Sentence:
    if sentence in stopwords:
        continue

    if sentence in terms:
        terms[sentence] += 1
    else:
        terms[sentence] = 1

print(Counter(terms))


artDf = pd.DataFrame.from_dict(terms, orient='index', columns=['詞頻'])
artDf.sort_values(by=['詞頻'], ascending=False)


img = "color-0"
img_path = "/Users/zhonghonghao/googlenews-wordCloud/%s.png" % img

mask_color = np.array(Image.open(img_path))
mask_color = mask_color[::3, ::3]
mask_image = mask_color.copy()
mask_image[mask_image.sum(axis=2) == 0] = 255

edges = np.mean([gaussian_gradient_magnitude(mask_color[:, :, i] / 255., 2) for i in range(3)], axis=0)
mask_image[edges > .08] = 255

wc = WordCloud(font_path="/Users/zhonghonghao/Downloads/ThePeakFontBeta_V0_101/ThePeakFontBeta_V0_101.ttf",
               mask=mask_color,
               max_font_size=35,
               max_words=4000,
               stopwords=stopwords,
               margin=0,
               relative_scaling=0,
               )

wc.generate(articleAll)
image_colors = ImageColorGenerator(mask_color)
wc.recolor(color_func=image_colors)

plt.imshow(wc, interpolation="bilinear")
plt.axis("off")
plt.figure(figsize=(25, 25))
plt.show()
