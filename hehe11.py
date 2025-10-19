
data_10 = data[:10]

# Thiết lập batch size
batch_size = 1000

# Thư mục lưu kết quả
os.makedirs("Result", exist_ok=True)

# Giả sử bạn muốn chạy từ batch đầu tiên
# Nếu cần bạn có thể thay đổi batch_start để tiếp tục từ batch khác.
batch_start = 0

for start_idx in range(batch_start * batch_size, len(data_10), batch_size):
    end_idx = min(start_idx + batch_size, len(data_10))
    batch_data = data_10.iloc[start_idx:end_idx].copy()

    results = []
    for idx in tqdm(range(len(batch_data)), desc=f"Processing batch {start_idx//batch_size}"):
        prompt = preprocess_conversations(batch_data.iloc[idx]['conversations'])
        
        messages = [
            [
                {"role": "system", "content": system_content},
                {"role": "user", "content": prompt}
            ]
        ]

        # Apply chat template
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        model_inputs = tokenizer(text, return_tensors="pt").to(device)

        # Generate responses
        generated_ids = model.generate(
            model_inputs.input_ids,
            max_new_tokens=512,
            eos_token_id=tokenizer.eos_token_id,
            temperature=0.25,
        )

        # Loại bỏ input_ids ra khỏi output để chỉ lấy phần model tạo ra
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        responses = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)

        for response in responses:
            output = clean_and_parse_json(response)
            results.append(output)

    batch_data['response'] = results

    batch_data_pd = pd.DataFrame(batch_data)
    batch_data_pd = batch_data_pd[['description', 'conversations', 'response']]
    batch_data_pd = batch_data_pd.applymap(
        lambda x: x.tolist() if isinstance(x, np.ndarray) else x
    )

    json_data = batch_data_pd.to_dict(orient='records')

    # Tạo tên file theo batch
    batch_index = start_idx // batch_size
    output_file_json = f"Result/result_batch_{batch_index}.json"
    output_file_parquet = f"Result/output_batch_{batch_index}.parquet"

    # Lưu file JSON
    with open(output_file_json, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)

    # Lưu file parquet
    batch_data.to_parquet(output_file_parquet, engine='pyarrow', index=False)

print("Hoàn thành việc xử lý và lưu dữ liệu theo batch.")




