import gzip
import os
import psycopg2
import shutil
import tempfile

# CONNECT DB
# Connect to PostgreSQL and return the connection object.
def connect_db():
    return psycopg2.connect(
        dbname=os.environ.get('DB_NAME'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASS'),
        host=os.environ.get('DB_HOST'),
        port=5432
    )


# CREATE QUERY FILE
# Creates and stores the query as a temporary file.
def create_query_file(data, query_titles, analysis_id):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.fasta') as query_file:
        for sequence in data['biological_sequences']:
            title = sequence.get('title', '')
            bases = sequence.get('bases')
            if bases:
                query_id = f"query_{len(query_titles) + 1}_{title}"
                query_titles[query_id] = title
                query_file.write(f">{query_id} {title}\n{bases}\n".encode())
        query_file_path = query_file.name

    storage_file_path = store_file(query_file_path, analysis_id, 'blastn_input')

    file_size = os.path.getsize(storage_file_path)
    print(f"Created query file: {storage_file_path} (Size: {file_size} bytes)")

    if file_size == 0:
        raise ValueError("Error - No valid sequences provided.")

    os.remove(query_file_path)

    return storage_file_path


# DECOMPRESS FILE
# Decompresses a .gz file and returns the path to the uncompressed file.
def decompress_file(compressed_file_path):
    decompressed_file_path = tempfile.NamedTemporaryFile(delete=False, suffix='.fasta').name
    with gzip.open(compressed_file_path, 'rb') as f_in, open(decompressed_file_path, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
    print(f"Decompressed file: {decompressed_file_path}")
    return decompressed_file_path


# LOADING FILES
# Similar functions which load files with slightly different specifications.

# LOAD NAMES
def load_names(names_file):
    names = {}
    with open(names_file) as f:
        for line in f:
            parts = line.strip().split('|')
            tax_id = parts[0].strip()
            name = parts[1].strip()
            name_class = parts[3].strip()
            if name_class == "scientific name":
                names[tax_id] = name
    print(f"Loaded Names from {names_file}, Total Entries: {len(names)}")
    return names


# LOAD NODES
def load_nodes(nodes_file):
    nodes = {}
    with open(nodes_file) as f:
        for line in f:
            parts = line.strip().split('|')
            tax_id = parts[0].strip()
            parent_id = parts[1].strip()
            rank = parts[2].strip()
            nodes[tax_id] = {'parent': parent_id, 'rank': rank}
    print(f"Loaded Nodes from {nodes_file}, Total Entries: {len(nodes)}")
    return nodes


# LOAD TAXID MAP
def load_taxid_map(taxid_map_file):
    taxid_map = {}
    with open(taxid_map_file) as f:
        for line in f:
            seq_id, tax_id = line.strip().split()
            taxid_map[seq_id] = tax_id
    print(f"Loaded TaxID map from {taxid_map_file}, Total Entries: {len(taxid_map)}")
    return taxid_map


# STORE FILE
# Store the compressed file in the shared volume.
def store_file(file_path, analysis_id, file_type):

    # Ensure this points to /mnt/data/blastn_storage
    output_dir = os.environ.get('STORAGE_FILE')
    if not output_dir:
        raise ValueError("Environment variable STORAGE_FILE is not set or is empty.")

    output_dir = os.path.join(output_dir, f"analysis_{analysis_id}")
    # Ensure the directory exists
    os.makedirs(output_dir, exist_ok=True) 

    compressed_file_path = os.path.join(output_dir, f"{file_type}.txt.gz")

    # Check if the file exists and then compress it
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} does not exist.")

    with open(file_path, 'rb') as f_in, gzip.open(compressed_file_path, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)

    if not os.path.exists(compressed_file_path):
        raise ValueError(f"Failed to store the file at {compressed_file_path}")

    # Return the path of the stored file in the shared volume
    return compressed_file_path
