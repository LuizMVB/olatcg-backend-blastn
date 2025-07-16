import json
import os
from .homology_analysis import perform_homology_analysis
from utils import connect_db, create_query_file, load_names, load_nodes, load_taxid_map


# BLASTN CALLBACK
# Called in main.py
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
            # Pass stored path to DB
            storage_query_file_path
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
        # Rollback transaction if something fails
        conn.rollback()
    except Exception as e:
        print(f"Error processing BLASTN job: {e}")
        update_analysis_status(conn, cursor, data['analysis_id'], 'EXECUTION_FAILED')
        conn.rollback()
    except:
        print('Error processing BLASTN job. Error Undetected')
        update_analysis_status(conn, cursor, data['analysis_id'], 'EXECUTION_FAILED')
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print('Job completed and acknowledged.')


# UPDATE ANALYSIS STATUS
# Defaults to 'EXECUTION_SUCCEEDED', in case of error, 'EXECUTION_FAILED' is to be passed as a parameter.
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