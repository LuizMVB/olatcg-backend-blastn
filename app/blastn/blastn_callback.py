import json
import os
from .homology_analysis import perform_homology_analysis
from utils import connect_db, create_query_file, load_names, load_nodes, load_taxid_map
from datetime import datetime


# BLASTN CALLBACK
# Called in main.py
def blastn_callback(ch, method, properties, body):
    print('Started processing BLASTN job...')

    data = json.loads(body)

    print(f'newdebug:\n{data}')

    conn = connect_db()
    cursor = conn.cursor()

    try:
        query_titles = {}

        # Generate and store query file
        storage_query_file_path = create_query_file(data, query_titles, data['analysis_id'])

        if not storage_query_file_path:
            raise ValueError("Failed to create and store query file.")
        
        print(f'Storage query file: {storage_query_file_path}')


        #cursor.execute("""
        #            UPDATE core_analysis
        #            SET
        #               updated_at = %s, 
        #               parameters = %s
        #            WHERE id = %s
        #            RETURNING id;
        #        """, (
        #    str(datetime.now()),
        #    json.dumps(data['parameters']),
        #    json.dumps(data['analysis_id']),
        #    # Pass stored path to DB
        #    #storage_query_file_path
        #))
        #blastn_input_id = cursor.fetchone()[0]

        blastn_input_id = data['analysis_id']
        

        # Load taxonomy data
        taxid_map = load_taxid_map(os.environ.get('TAXID_MAP_FILE'))
        nodes = load_nodes(os.environ.get('NODES_FILE'))
        names = load_names(os.environ.get('NAMES_FILE'))

        # Perform homology analysis and get output file path
        storage_output_fmt_11_file_path = perform_homology_analysis(
            conn, data, query_titles, storage_query_file_path, taxid_map, nodes, names)

        print(f'PHA OK')

        if not storage_output_fmt_11_file_path:
            raise ValueError("Failed to generate BLAST output.")

        print('Time to insert file into blastoutput... ')

        print(f'Time for insert:\nblastn_input_id: {blastn_input_id} | Type:{type(blastn_input_id)}\nsotrage_fmt_11: {storage_output_fmt_11_file_path} | Type: {type(storage_output_fmt_11_file_path)}')
        # Insert output file path into database
        #cursor.execute("""
        #                INSERT INTO core_analysisoutput (id, created_at, updated_at, results, file, input_id)
        #                VALUES (%s, %s, %s, %s, %s, %s);
        #            """, (blastn_input_id,
        #                  datetime.now(),
        #                  datetime.now(),
        #                  {'placeholder'},
        #                  storage_output_fmt_11_file_path,
        #                  json.dumps(data['analysis_id'])))
        #conn.commit()

        print(f'cursor_analysisoutput OK')

        update_analysis_status(conn, cursor, data['analysis_id'])

        print(f'up_analysis_status OK')


        print('Finished processing BLASTN job.')
    except FileNotFoundError as fe:
        print(f"Missing file: {fe}")
        update_analysis_status(conn, cursor, data['analysis_id'], 'FAILED')
        # Rollback transaction if something fails
        conn.rollback()
    except Exception as e:
        print(f"Error processing BLASTN job: {e}")
        update_analysis_status(conn, cursor, data['analysis_id'], 'FAILED')
        conn.rollback()
    except:
        print('Error processing BLASTN job. Error Undetected')
        update_analysis_status(conn, cursor, data['analysis_id'], 'FAILED')
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print('Job completed and acknowledged.')


# UPDATE ANALYSIS STATUS
# Defaults to 'SUCCEEDED', in case of error, 'FAILED' is to be passed as a parameter.
def update_analysis_status(conn, cursor, analysis_id, status="SUCCEEDED"):

    # Execute the update statement
    cursor.execute("""
                UPDATE core_analysis
                SET status = %s
                WHERE id = %s
            """, (status, analysis_id))
    
    # Commit the transaction
    conn.commit()
    print(f"Successfully updated analysis_id {analysis_id} to {status}.")