import csv

# 입력 CSV 파일과 출력 TXT 파일 경로 설정
input_csv = 'merged_details.csv'
output_txt = 'Merged_details.txt'

# 장르에서 첫 단어로 설정할 키워드 목록
genre_keywords = ['드라마', '영화', '애니메이션']

# 텍스트 파일을 쓰기 모드로 열기
with open(input_csv, 'r', encoding='utf-8') as csvfile, open(output_txt, 'w', encoding='utf-8') as txtfile:
    reader = csv.DictReader(csvfile)
    
    for row in reader:
        # 제목과 연도 추출
        title_with_year = row['Title']
        if '(' in title_with_year and ')' in title_with_year:
            year = title_with_year.split('(')[-1].strip(')')
            title_clean = title_with_year.split('(')[0].strip()
        else:
            # 연도가 없는 경우 기본값 설정
            year = '알 수 없음'
            title_clean = title_with_year.strip()
        
        # 장르 처리
        genres = row['Genre'].replace('"', '').split(', ')
        
        # 첫 단어 설정
        first_word = '영화'  # 기본값을 '영화'로 설정
        for keyword in genre_keywords:
            if keyword in genres:
                first_word = keyword
                break
        
        # 장르 목록에서 '드라마', '영화', '애니메이션' 제외
        filtered_genres = [genre for genre in genres if genre not in genre_keywords]
        genre_str = ', '.join(filtered_genres) if filtered_genres else '장르 정보 없음'
        
        # 나머지 필드 추출
        imdb_rating = row['Rating IMDB'].strip()
        tomato_rating = row['Rating TOMATO'].strip()
        age_rating = row['Age Rating'].strip()
        production_country = row['Production Country'].strip()
        ott = row['OTT'].strip()
        
        # 연령 등급에 '세' 추가 (숫자만 있을 경우)
        if age_rating.isdigit():
            age_rating += '세'
        
        # 원하는 형식으로 문자열 구성
        formatted_text = (
            f"{first_word} 제목은 {title_clean}이고 {year}년에 개봉했습니다. "
            f"장르는 {genre_str}입니다. "
            f"IMDB 평점은 {imdb_rating}점이고, 토마토 평점은 {tomato_rating}점입니다. "
            f"해당 영상물의 연령 등급은 {age_rating}이고, 제작 국가는 {production_country}입니다. "
            f"마지막으로 해당 영상물을 시청할 수 있는 OTT는 {ott}입니다.\n"
        )
        
        # 텍스트 파일에 작성
        txtfile.write(formatted_text)

print(f"모든 데이터가 '{output_txt}' 파일에 성공적으로 저장되었습니다.")
