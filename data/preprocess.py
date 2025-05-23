import json
import os
import pandas as pd

USING_BLIP = False
path = '../collect_data/raw_data.jsonl'
with open(path, 'r') as f:
    data = f.readlines()

# Preprocess, the 'raw_data.jsonl' on this repository has been preprocessed.
# remove_highlights = [
#     "When buying this unisex item, keep in mind that it is graded in standard men's sizing",
#     "Product is already available to be shipped",
#     "Release date: ",
#     "This product is crafted from upcycled materials",
#     "authenticity QR code",
#     'Any differences between the piece pictured and the one you receive are',
#     'Be mindful to try on swimwear over your',
#     'Be sure before opening',
#     'C.P. Company suggests removing any detachable accessories before washing',
#     'Decorated with rips and paint splatter detail - both created by hand - this pair of ',
#     'Just a reminder that this piece must be tried o',
#     'Learn more about what makes',
#     'Original box included',
#     'The full look includes',
#     'The item you receive may differ slightly',
#     'These styles are supplied by a premium sneaker marketplace',
#     'This item comes with',
#     'This piece ',
#     'This item is made from at least 50% organic materials'
# ]

# remove_compositions = [
#     'RDS Product Name'
# ]

# dataset = []
# t = set()

# for i, row in enumerate(data):
#     row = json.loads(row)

#     # Xử lý brand
#     if row.get('brand', '').lower() == 'our legacy':
#         row['brand'] = ''

#     # Xử lý highlights
#     new_highlights = set()
#     for highlight in row.get('highlights', []):
#         new_highlights.update(highlight.strip().split('\n'))
#     filtered_highlights = []
#     for highlight in new_highlights:
#         if not any(h.lower() in highlight.lower() for h in remove_highlights):
#             filtered_highlights.append(highlight)
#             if '.' in highlight:
#                 t.add(highlight)
#     row['highlights'] = filtered_highlights

#     # Xử lý composition
#     new_compositions = set()
#     for comp in row.get('composition', []):
#         new_compositions.update(comp.strip().split('\n'))
#     filtered_compositions = []
#     for comp in new_compositions:
#         if not any(c.lower() in comp.lower() for c in remove_compositions):
#             if ':' in comp:
#                 # bỏ nếu có dấu ":" (nếu cần giữ lại thì xóa dòng này)
#                 continue
#             filtered_compositions.append(comp)
#             if '.' in comp:
#                 t.add(comp)
#     row['composition'] = filtered_compositions

#     # Thêm dòng JSON đã xử lý vào dataset
#     dataset.append(json.dumps(row, ensure_ascii=False) + '\n')

# with open(path, 'w') as f:
#     f.writelines(dataset)

# Create metadata.csv file
with open(path, 'r') as f:
    data = f.readlines()
    
DATA_FOLDER = '../data'
os.makedirs(DATA_FOLDER, exist_ok=True)

clean_data_path = os.path.join(DATA_FOLDER, 'clean_data.csv' if USING_BLIP else 'clean_data_no_blip.csv')

clean_data = []
for row in data:
    element = []
    row = json.loads(row)
    element.extend([row['category'].strip(), row['name'].strip()])
    element.extend(row['highlights'])
    try:
        while element.index(''):
            element.remove('')
    except:
        pass
    caption = ', '.join(element).lower()
    if USING_BLIP:
        for image_url in row['image_urls']:
            new_row = f'{image_url},{image_url.split("/")[-1]},"{caption}"\n'
            clean_data.append(new_row)
    else:
        new_row = f'{row["image_urls"][0]},{row["image_urls"].split("/")[-1]},"{caption}"\n'
        clean_data.append(new_row)
        
with open(clean_data_path, 'w') as f:
    f.write('image_url,file_name,prompt\n')
    f.writelines(clean_data)
    
data = pd.read_csv(clean_data_path)
data = data.drop_duplicates(subset='image_url', keep='first')
data.to_csv(clean_data_path)