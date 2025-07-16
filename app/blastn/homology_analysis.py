import os
import subprocess
import tempfile
from utils import decompress_file, store_file

# FORMAT BLAST OUTPUTs
# Formats the BLAST output using blast_formatter and writes it to a file.
def format_blast_output(analysis_id, blast_output_path):

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


# GET LINEAGE
# Uses the Taxonomy ID to assign lineage to a subject. 
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


# PARSE BLAST RESULTS
# Uses the output of 'run_blast'.
# Called in 'perform_homology_analysis'.
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

                # If we already have a hit for this query_id, skip further hits
                if query_id in parsed_results:
                    continue

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

            parsed_results[query_id] = {
                'query_id': query_id,
                'query_title': query_titles.get(query_id, ''),
                'query_len': hit['query_length'],
                'hits': [hit]
            }

    cursor.close()
    os.remove(decompressed_fmt_6_file_path)


# PERFORM HOMOLOGY ANALYSIS
# Called in 'blastn_callback' to perform homology analysis and generate output file path.
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


# RUN BLAST
# Runs BLAST and stores output in a temporary file.
# 'Gap Open', 'Gap Extend' and 'Penalty' are currently not in use.
# Unclear what 'Penalty' refers to, change naming later.
def run_blast(query_file_path, analysis_id, db, evalue, gapopen, gapextend, penalty):

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