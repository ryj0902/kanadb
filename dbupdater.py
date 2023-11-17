import os
import pandas as pd
from tqdm import tqdm
from sqlalchemy import text, create_engine

card_table = pd.read_json('data/TextAsset/CARD_TABLE.txt', encoding='utf8')
card_table2 = pd.read_json('data/TextAsset/CARD_TABLE2.txt', encoding='utf8')
string = pd.read_json('data/TextAsset/STRING.txt', encoding='utf8')
product_table = pd.read_json('data/TextAsset/PRODUCT_TABLE.txt', encoding='utf8')

# 정렬 순서를 위한 별도의 맵핑
category_map = {'CHARACTER': 1,
                'SPELL': 2,
                'FOLLOWER': 3,}

rarity_map = {'UNCOMMON': '언커먼',
              'COMMON': '커먼',
              'SUPERIOR': '슈페리어',
              'RARE': '레어',
              'DOUBLE_RARE': '더블레어',
              'UNIQUE': '유니크'}

# 정렬 순서를 위한 별도의 맵핑
theme_map = {'PUBLIC': 1,
             'PRIVATE': 2,
             'CRUX': 3,
             'DARK_LORE': 4,
             'INDEPENDENCE': 5}

df = pd.DataFrame(columns=['id', 'name', 'category', 'rarity', 'theme', 'tag', 'episode', 'point', 'size', 'atk', 'defs', 'hp', 'limit', 'frame', 'collect', 'desc', 'skill_turn', 'skill_instance', 'skill_attack', 'skill_defend', 'link'])

card_list = list()
for card in tqdm(card_table.itertuples(), total=len(card_table)):
    temp = dict()
    id = card.CARD_ID
    if id % 10 != 0: # drop enhanced card
        continue
    temp['id'] = id
    name = card_table2.loc[card_table2['CARD_ID'] == id]['CARD_NAME'].item()
    temp['name'] = string.loc[string['STRING_NAME'] == name]['STRING_KR'].item()
    # omit image file not found
    if not os.path.exists(f'data/Texture2D/CARD_{id}.png'):
        print(id, temp['name'])
        continue
    temp['category'] = category_map[card.CARD_CATEGORY]
    temp['rarity'] = rarity_map[card.CARD_RARITY]
    temp['theme'] = theme_map[card.CARD_THEME]
    tags = card.CARD_TAG
    tags_str = list()
    for tag in tags:
        try:
            tag = string.loc[string['STRING_NAME'] == tag]['STRING_KR'].item()
            tags_str.append(tag)
        except Exception as e:
            print(id, temp['name'], tags, tag)
            print(e)
        finally:
            pass
    temp['tag'] = ','.join(tags_str)
    episode = card.CARD_EPISODE
    prefix = 100 if episode[1] == 'P' else 500
    episode = prefix + int(episode[2:])
    temp['episode'] = episode
    temp['point'] = card.CARD_POINT
    temp['size'] = card.CARD_SIZE
    temp['atk'] = card.CARD_ATK
    temp['defs'] = card.CARD_DEF
    temp['hp'] = card.CARD_HP
    temp['limit'] = card.CARD_LIMIT
    temp['frame'] = card.CARD_FRAME
    temp['collect'] = card.CARD_COLLECT
    desc = card_table2.loc[card_table2['CARD_ID'] == id]['CARD_DESC'].item()
    temp['desc'] = string.loc[string['STRING_NAME'] == desc]['STRING_KR'].item()
    skill_turn_str = list()
    skills = card_table2.loc[card_table2['CARD_ID'] == id]['CARD_SKILL_TURN'].item()
    for skill in skills:
        if skill == -1:
            break
        skill = string.loc[string['STRING_NAME'] == f'SKILL_TEXT_{skill}']['STRING_KR'].item()
        skill_turn_str.append(skill)
    temp['skill_turn'] = '\n'.join(skill_turn_str)
    skill_instance_str = list()
    skills = card_table2.loc[card_table2['CARD_ID'] == id]['CARD_SKILL_INSTANCE'].item()
    for skill in skills:
        if skill == -1:
            break
        skill = string.loc[string['STRING_NAME'] == f'SKILL_TEXT_{skill}']['STRING_KR'].item()
        skill_instance_str.append(skill)
    temp['skill_instance'] = '\n'.join(skill_instance_str)
    skill_attack_str = list()
    skills = card_table2.loc[card_table2['CARD_ID'] == id]['CARD_SKILL_ATTACK'].item()
    for skill in skills:
        if skill == -1:
            break
        skill = string.loc[string['STRING_NAME'] == f'SKILL_TEXT_{skill}']['STRING_KR'].item()
        skill_attack_str.append(skill)
    temp['skill_attack'] = '\n'.join(skill_attack_str)
    skill_defend_str = list()
    skills = card_table2.loc[card_table2['CARD_ID'] == id]['CARD_SKILL_DEFEND'].item()
    for skill in skills:
        if skill == -1:
            break
        skill = string.loc[string['STRING_NAME'] == f'SKILL_TEXT_{skill}']['STRING_KR'].item()
        skill_defend_str.append(skill)
    temp['skill_defend'] = '\n'.join(skill_defend_str)
    link = card_table2.loc[card_table2['CARD_ID'] == id]['CARD_LINK'].item()
    link = list(map(lambda x: str(x), link))
    temp['link'] = ','.join(link)
    producible = product_table.loc[product_table['PRODUCT_ID'] == id]['PRODUCT_MATERIAL1'].item()
    producible = True if producible != -1 else False
    temp['producible'] = producible

    card_list.append(temp)

df = pd.DataFrame(card_list)

db_data = f'mysql+pymysql://root:{os.environ["DB_PW"]}@localhost:3306/kanadb?charset=utf8'
engine = create_engine(db_data)

with engine.begin() as conn:
    df.to_sql('card_card', conn, if_exists='replace', index=False)

engine.dispose()