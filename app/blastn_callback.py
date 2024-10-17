import os
import tempfile
import subprocess
import psycopg2
import shutil
import gzip
import json

def connect_db():
    """Connect to PostgreSQL and return the connection object."""
    return psycopg2.connect(
        dbname=os.environ.get('DB_NAME'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASS'),
        host=os.environ.get('DB_HOST'),
        port=5432
    )

def store_file(file_path, analysis_id, file_type):
    """Store the compressed file in the shared volume."""
    output_dir = os.environ.get('STORAGE_FILE')  # Ensure this points to /mnt/data/blastn_storage
    if not output_dir:
        raise ValueError("Environment variable STORAGE_FILE is not set or is empty.")

    output_dir = os.path.join(output_dir, f"analysis_{analysis_id}")
    os.makedirs(output_dir, exist_ok=True)  # Ensure the directory exists

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

def decompress_file(compressed_file_path):
    """Decompresses a .gz file and returns the path to the uncompressed file."""
    decompressed_file_path = tempfile.NamedTemporaryFile(delete=False, suffix='.fasta').name
    with gzip.open(compressed_file_path, 'rb') as f_in, open(decompressed_file_path, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
    print(f"Decompressed file: {decompressed_file_path}")
    return decompressed_file_path

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

def run_blast(query_file_path, analysis_id, db, evalue, gapopen, gapextend, penalty):
    """Runs BLAST and stores output in a temporary file."""

    # Decompress the stored .gz query file
    decompressed_query_file = decompress_file(query_file_path)

    with tempfile.NamedTemporaryFile(delete=False, suffix='.out') as output_file:
        output_file_path = output_file.name

    blastn_command = [
        'blastn',
        '-query', decompressed_query_file,
        '-db', db,
        '-evalue', str(evalue),
        # '-gapopen', str(gapopen),
        # '-gapextend', str(gapextend),
        # '-penalty', str(penalty),
        '-outfmt', '11',  # Output format 11 (BLAST archive)
        '-max_target_seqs', '1',
        '-out', output_file_path  # Directly output to the file
    ]

    print(f"Running BLAST command: {' '.join(blastn_command)}")

    with open(output_file_path, 'w') as blast_output:
        result = subprocess.run(blastn_command, stdout=blast_output, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            print(f"BLAST Error: {result.stderr}")
            raise subprocess.CalledProcessError(result.returncode, blastn_command, output=result.stdout,
                                                stderr=result.stderr)

    # Clean up decompressed file
    os.remove(decompressed_query_file)

    storage_file_path = store_file(output_file_path, analysis_id, 'blastn_output_fmt_11')

    file_size = os.path.getsize(storage_file_path)
    print(f"Created output file: {storage_file_path} (Size: {file_size} bytes)")

    if file_size == 0:
        raise ValueError("Error - No valid output provided.")

    os.remove(output_file_path)

    print(f"BLAST completed, output stored in: {storage_file_path}")
    return storage_file_path

def load_taxid_map(taxid_map_file):
    taxid_map = {}
    with open(taxid_map_file) as f:
        for line in f:
            seq_id, tax_id = line.strip().split()
            taxid_map[seq_id] = tax_id
    print(f"Loaded TaxID map from {taxid_map_file}, Total Entries: {len(taxid_map)}")
    return taxid_map


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

def format_blast_output(analysis_id, blast_output_path):
    """Formats the BLAST output using blast_formatter and writes it to a file."""

    # Decompress the stored .gz blast output file
    decompressed_output_file = decompress_file(blast_output_path)

    with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as formatted_output_file:
        formatted_output_path = formatted_output_file.name

    blast_formatter_command = [
        'blast_formatter',
        '-archive', decompressed_output_file,
        '-outfmt', '6 qseqid sseqid pident length qlen slen score evalue qseq sseq',
        '-out', formatted_output_path  # Directly output to the file
    ]

    print(f"Running BLAST Formatter command: {' '.join(blast_formatter_command)}")

    with open(formatted_output_path, 'w') as formatted_output:
        result = subprocess.run(blast_formatter_command, stdout=formatted_output, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            print(f"BLAST Formatter Error: {result.stderr}")
            raise subprocess.CalledProcessError(result.returncode, blast_formatter_command, stderr=result.stderr)

    # Clean up decompressed file
    os.remove(decompressed_output_file)

    storage_file_path = store_file(formatted_output_path, analysis_id, 'blastn_output_fmt_6')

    os.remove(formatted_output_path)

    print(f"BLAST Formatter completed, formatted output stored in: {storage_file_path}")

    return storage_file_path

def get_lineage(subject_id, tax_id, nodes, names):
    lineage = []

    if not tax_id:
        lineage.append('unknown')
        print(f"Assigning 'unknown' taxonomy for subject_id {subject_id} and tax_id {tax_id}.")

    while tax_id != '1':  # Continue while tax_id is not root
        name = names.get(tax_id, 'unknown')
        lineage.append(name)
        if tax_id not in nodes:
            break  # Stop if tax_id not found in nodes
        parent_id = nodes[tax_id]['parent']
        tax_id = parent_id

    return '; '.join(lineage[::-1])

def parse_blast_results(conn, analysis_id, blast_outfmt11_path, query_titles, taxid_map, nodes, names):
    cursor = conn.cursor()

    # Step 1: Format the BLAST output using the blast_formatter command
    storage_output_fmt_6_file_path = format_blast_output(analysis_id, blast_outfmt11_path)

    print(f"Parsing BLAST results from {storage_output_fmt_6_file_path}")

    # Decompress the BLAST output .gz file before reading
    decompressed_fmt_6_file_path = decompress_file(storage_output_fmt_6_file_path)

    # Parsed results to return
    parsed_results = {}

    with open(decompressed_fmt_6_file_path, 'r') as blast_results_file:
        for line_number, line in enumerate(blast_results_file, 1):
            cols = line.strip().split("\t")

            print(f"Line {line_number}: Parsed {len(cols)} columns.")

            try:
                query_id = cols[0]

                # Safely split subject_id and handle cases where there's no pipe ('|')
                subject_id_parts = cols[1].split('|')

                # If the split does not result in at least two parts, assign 'unknown'
                if len(subject_id_parts) > 1:
                    subject_id = subject_id_parts[1]
                else:
                    subject_id = cols[1]  # Fall back to the entire value if no pipe present

                # Get taxonomy ID and assign 'unknown' if not found
                tax_id = taxid_map.get(subject_id, None)

                # If the taxonomy ID is "unknown", assign the unknown lineage
                lineage = get_lineage(subject_id, tax_id, nodes, names)

            except IndexError as e:
                print(f"Error processing line {line_number}: {line.strip()}")
                raise e  # Re-raise the error to handle it properly

            # Step 1: Insert Taxonomy and get its ID
            insert_taxonomy_sql = """
                INSERT INTO core_taxonomy (external_tax_id, title, lineage, analysis_id)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
            """
            cursor.execute(insert_taxonomy_sql, (tax_id, f'{subject_id}|{tax_id}', lineage, analysis_id))
            taxonomy_id = cursor.fetchone()[0]

            # Step 2: Insert Alignment and get its ID
            insert_alignment_sql = """
                INSERT INTO core_alignment (taxonomy_id, analysis_id)
                VALUES (%s, %s)
                RETURNING id;
            """
            cursor.execute(insert_alignment_sql, (taxonomy_id, analysis_id))
            alignment_id = cursor.fetchone()[0]

            # Step 3: Insert Biological Sequences (Query and Subject sequences)
            insert_biological_seq_sql = """
                INSERT INTO core_biologicalsequence (alignment_id, bases, external_sequence_id, type)
                VALUES (%s, %s, %s, %s);
            """
            cursor.execute(insert_biological_seq_sql, (alignment_id, cols[8], query_id, 'GAPPED_DNA'))
            cursor.execute(insert_biological_seq_sql, (alignment_id, cols[9], subject_id, 'GAPPED_DNA'))

            # Commit the transaction after each insertion to ensure consistency
            conn.commit()

            hit = {
                'subject_id': cols[1],
                'tax_id': tax_id,
                'lineage': lineage,
                'percent_identity': float(cols[2]),
                'alignment_length': int(cols[3]),
                'query_length': int(cols[4]),
                'subject_length': int(cols[5]),
                'score': float(cols[6]),
                'evalue': float(cols[7]),
                'query_sequence': cols[8],
                'subject_sequence': cols[9],
            }

            if query_id not in parsed_results:
                parsed_results[query_id] = {
                    'query_id': query_id,
                    'query_title': query_titles.get(query_id, ''),
                    'query_len': hit['query_length'],
                    'hits': []
                }

            parsed_results[query_id]['hits'].append(hit)

    cursor.close()
    os.remove(decompressed_fmt_6_file_path)

def perform_homology_analysis(conn, data, query_titles, query_file_path, taxid_map, nodes, names):
    storage_output_fmt_11_file_path = run_blast(query_file_path,
                                                data['analysis_id'],
                                                data['database'],
                                                data['evalue'],
                                                data['gap_open'],
                                                data['gap_extend'],
                                                data['penalty'])

    parse_blast_results(conn, data['analysis_id'],
                        storage_output_fmt_11_file_path,
                        query_titles, taxid_map,
                        nodes, names)

    return storage_output_fmt_11_file_path


def blastn_callback(ch, method, properties, body):
    print('Started processing BLASTN job...')

    data = json.loads(body)

    conn = connect_db()
    cursor = conn.cursor()

    try:
        query_titles = {}

        # Generate and store query file
        storage_query_file_path = create_query_file(data, query_titles, data['analysis_id'])

        if not storage_query_file_path:
            raise ValueError("Failed to create and store query file.")

        cursor.execute("""
                    INSERT INTO core_blastninput (database, evalue, gap_open, gap_extend, penalty, analysis_id, input_file)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id;
                """, (
            data['database'], data['evalue'], data['gap_open'],
            data['gap_extend'], data['penalty'], data['analysis_id'],
            storage_query_file_path  # Pass stored path to DB
        ))
        blastn_input_id = cursor.fetchone()[0]
        conn.commit()

        # Load taxonomy data
        taxid_map = load_taxid_map(os.environ.get('TAXID_MAP_FILE'))
        nodes = load_nodes(os.environ.get('NODES_FILE'))
        names = load_names(os.environ.get('NAMES_FILE'))

        # Perform homology analysis and get output file path
        storage_output_fmt_11_file_path = perform_homology_analysis(
            conn, data, query_titles, storage_query_file_path, taxid_map, nodes, names)

        if not storage_output_fmt_11_file_path:
            raise ValueError("Failed to generate BLAST output.")

        print('Time to insert file into blastoutput... ')

        # Insert output file path into database
        cursor.execute("""
                        INSERT INTO core_blastnoutput (input_id, output_file)
                        VALUES (%s, %s);
                    """, (blastn_input_id, storage_output_fmt_11_file_path))
        conn.commit()

        update_analysis_status(conn, cursor, data['analysis_id'])

        print('Finished processing BLASTN job.')
    except FileNotFoundError as fe:
        print(f"Missing file: {fe}")
        update_analysis_status(conn, cursor, data['analysis_id'], 'EXECUTION_FAILED')
        conn.rollback()  # Rollback transaction if something fails
    except Exception as e:
        print(f"Error processing BLASTN job: {e}")
        update_analysis_status(conn, cursor, data['analysis_id'], 'EXECUTION_FAILED')
        conn.rollback()  # Rollback transaction if something fails
    except:
        print('Error processing BLASTN job. Error Undetected')
        update_analysis_status(conn, cursor, data['analysis_id'], 'EXECUTION_FAILED')
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print('Job completed and acknowledged.')


def update_analysis_status(conn, cursor, analysis_id, status="EXECUTION_SUCCEEDED"):
    # Execute the update statement
    cursor.execute("""
                UPDATE core_analysis
                SET status = %s
                WHERE id = %s
            """, (status, analysis_id))
    # Commit the transaction
    conn.commit()
    print(f"Successfully updated analysis_id {analysis_id} to {status}.")

