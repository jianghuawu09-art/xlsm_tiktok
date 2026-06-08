import urllib.request, ssl
urls=[
    "https://img-reg-ab.imagency.cn/e/fc1a6e2defcf2c6cddeb40a2df1de63a.jpg",
    "https://img-reg-ab.imagency.cn/e/6f100ed0b52f05d5562de86e59c72715.jpg",
    "https://img-reg-ab.imagency.cn/e/e60b492cdf9214f836d3e97bc713db58.jpg",
    "https://img-reg-ab.imagency.cn/e/f444a920d7e9a3862a2740d8fc608fbe.png",
]
ctx=ssl.create_default_context()
ctx.check_hostname=False
ctx.verify_mode=ssl.CERT_NONE
for u in urls:
    try:
        r=urllib.request.urlopen(u, timeout=10, context=ctx)
        b=r.read()
        print(u, r.status, r.getheader('Content-Type'), len(b))
    except Exception as e:
        print('ERR', u, repr(e))
