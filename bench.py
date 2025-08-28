import argparse
import re
import time
from typing import Dict, List, Optional, Union

import requests


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='HTTP server availability testing tool',
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-H', '--hosts',
        type=str,
        help='Comma-separated list of hosts without spaces',
    )
    group.add_argument(
        '-F', '--file',
        type=str,
        help='Path to file with hosts list',
    )
    parser.add_argument(
        '-C', '--count',
        type=int,
        default=1,
        help='Number of requests per host (default: 1)',
    )
    parser.add_argument(
        '-O', '--output',
        type=str,
        help='Path to output file',
    )
    return parser.parse_args()


def read_hosts_from_file(file_path: str) -> List[str]:

    try:
        with open(file_path, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f'Error: File "{file_path}" not found')
        return []
    except IOError as e:
        print(f'Error reading file "{file_path}": {e}')
        return []


def validate_url(url: str) -> bool:
    pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}'  # domain
        r'(:\d+)?'  # port
        r'(/.*)?$'  # path
    )
    return bool(pattern.match(url))


def validate_count(count: int) -> bool:
    return count >= 1


def make_request(url: str) -> Dict[str, Union[float, bool, Optional[str]]]:
    start_time = time.time()
    try:
        response = requests.get(url, timeout=10)
        elapsed = time.time() - start_time

        return {
            'time': elapsed,
            'success': response.status_code < 400,
            'error': None,
        }
    except requests.exceptions.RequestException as e:
        return {
            'time': 0,
            'success': False,
            'error': str(e),
        }


def calculate_statistics(
    results: List[Dict[str, Union[float, bool, Optional[str]]]]
) -> Dict[str, Union[int, float]]:
    times = [r['time'] for r in results if r['success']]
    errors = sum(1 for r in results if not r['success'] and r['error'])
    failed = sum(1 for r in results if not r['success'] and not r['error'])

    return {
        'success': len(times),
        'failed': failed,
        'errors': errors,
        'min_time': min(times) if times else 0,
        'max_time': max(times) if times else 0,
        'avg_time': sum(times) / len(times) if times else 0,
    }


def print_results(
    stats: Dict[str, Dict[str, Union[int, float]]],
    output_file: Optional[str] = None
) -> None:
    output = []
    for host, data in stats.items():
        output.append(f'Host: {host}')
        output.append(f'  Success: {data["success"]}')
        output.append(f'  Failed: {data["failed"]}')
        output.append(f'  Errors: {data["errors"]}')
        output.append(f'  Min time: {data["min_time"]:.3f}s')
        output.append(f'  Max time: {data["max_time"]:.3f}s')
        output.append(f'  Avg time: {data["avg_time"]:.3f}s')
        output.append('')

    result = '\n'.join(output)

    if output_file:
        with open(output_file, 'w') as f:
            f.write(result)
    else:
        print(result)


def main() -> None:
    try:
        args = parse_arguments()
        hosts: List[str] = []

        if args.hosts:
            hosts = args.hosts.split(',')
        else:
            hosts = read_hosts_from_file(args.file)
            if not hosts:
                return

        if not validate_count(args.count):
            print('Count must be a positive integer.')
            return

        valid_hosts: List[str] = []
        invalid_hosts: List[str] = []

        for host in hosts:
            if validate_url(host):
                valid_hosts.append(host)
            else:
                invalid_hosts.append(host)
                print(f'Warning: Invalid URL format "{host}" - skipping.')

        if not valid_hosts:
            print('No valid hosts to test.')
            return

        stats: Dict[str, Dict[str, Union[int, float]]] = {}
        for host in valid_hosts:
            results: List[Dict[str, Union[float, bool, Optional[str]]]] = []
            print(f'Testing {host}...')

            for _ in range(args.count):
                results.append(make_request(host))
                time.sleep(1)

            stats[host] = calculate_statistics(results)

        print_results(stats, args.output)

        if invalid_hosts:
            print(f'Skipped {len(invalid_hosts)} invalid hosts:')
            for host in invalid_hosts:
                print(f'  {host}')

    except KeyboardInterrupt:
        print('Testing interrupted by user')
    except Exception as e:
        print(f'Unexpected error: {e}')


if __name__ == '__main__':
    main()
