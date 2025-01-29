import asyncio

async def generate_mikuji(fortune,generator):
    output = await asyncio.to_thread(
                generator,
                f"今日の運勢は「{fortune}」だ！ラッキーカラーは",
                    max_length = 100,
                    num_return_sequences = 1,
                    truncation = True,
                    no_repeat_ngram_size = 2,
                    #early_stopping = True,
                    temperature = 0.5,
                    top_k = 50,
                    top_p = 0.8,
                    eos_token_id = 50256,
                    return_full_text = False
                )
    #print(output[0]["generated_text"])
    return(output[0]["generated_text"])