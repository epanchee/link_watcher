from daemon import FetchDaemon
from fetcher.agents import FetchItem, FetchAgent
from fetcher.serializing import JsonSerializer
from fetcher.storing import MultipleSaveDriver, StdoutDriver, TextDriver

floor = FetchItem(xpath='/html/body/div[2]/section/div[2]/div[2]/div[1]/div[1]/div[4]')
flat1 = FetchItem(xpath='/html/body/div[2]/section/div[2]/div[2]/div[1]/div[2]/div/div[7]/div[4]',
                  name='flat1', related=floor)
floor = FetchItem(xpath='/html/body/div[2]/section/div[2]/div[2]/div[1]/div[1]/div[2]')
flat2 = FetchItem(xpath='/html/body/div[2]/section/div[2]/div[2]/div[1]/div[2]/div/div[7]/div[2]',
                  name='flat2', related=floor)

atomstroy = FetchAgent(
    url='https://www.atomstroy.net/zhilaya_nedvizhimost/art-gorod-park/ceny-i-nalichie',
    fetch_items=[flat1, flat2]
)

fd = FetchDaemon(
    agent=atomstroy,
    output_driver=MultipleSaveDriver(drivers=[
        StdoutDriver(),
        TextDriver(serializer=JsonSerializer, path='/tmp/fetcher.out')
    ]),
    interval=10
)

fd.start()
