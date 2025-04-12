import asyncio
import edge_tts

async def run():
    try:
        voices = await edge_tts.VoicesManager.create()
        print(f"Found {len(voices.voices)} voices")
        for i, voice in enumerate(voices.voices[:10]):
            print(f"{i+1}. {voice['ShortName']} - {voice['Gender']} - {voice['Locale']}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(run())
