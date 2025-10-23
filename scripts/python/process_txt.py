import os

companies = ["Amazon", "Apple", "Facebook", "Google", "Microsoft"]

# input_file = "/opt/airflow/output/wiki_pages"
OUTPUT_FILE = "/opt/airflow/output/filtered_wiki_pages.csv"

def transform_txt_file(**kwargs):
    try:
        ti = kwargs['ti']
        input_file = ti.xcom_pull(task_ids='download_wiki')
        
        if not input_file or not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found or XCom was empty: {input_file}")
        
        print(f"Transforming data from: {input_file}")
        print(f"Writing filtered data to: {OUTPUT_FILE}")
        
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as infile, open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
            outfile.write("project,page_title,view_count\n")
            
            count = 0
            for line in infile:
                parts = line.strip().split(" ")
                if len(parts) < 3:
                    continue
                
                project, page_title, view_count = parts[0], parts[1], parts[2]
                
                if page_title in companies:
                    outfile.write(f"{project},{page_title},{view_count}\n")
                    count +=1
        print(f"Transformation complete. Found {count} matching entries.")
        
        # Return the path to the new CSV file. This pushes it to XCom
        # for the next task ('load_db') to use.
        return OUTPUT_FILE
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise