import argparse
from ingest_session import ingest_session

def main():
    parser = argparse.ArgumentParser(description='Ingest a full F1 race weekend')
    parser.add_argument('--season', type=int, required=True)
    parser.add_argument('--round', type=int, required=True)
    args = parser.parse_args()

    print(f"Ingesting season {args.season} round {args.round}")

    for session_type in ['Q', 'R']:
        try:
            ingest_session(args.season, args.round, session_type)
        except Exception as e:
            print(f"Failed to ingest {session_type}: {e}")

if __name__ == "__main__":
    main()