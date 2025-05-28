import asyncio
from crawl4ai import *


async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://dribbble.com/shots/25938309-Mobile-Banking-App",
        )
        print(result.markdown)


if __name__ == "__main__":
    asyncio.run(main())
