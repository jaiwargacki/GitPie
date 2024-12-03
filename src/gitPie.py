"""
Create a pie chart of authors contributions to current lines of code in a git repository.
This script uses git blame to get the authors of each line in the repository.
The pie chart shows the percentage of lines contributed by each author.
Authors and the number of lines they contributed can be saved to a file.
Authors can be loaded from a file to skip the git blame step.
@author: Jai Wargacki
"""

import argparse
import subprocess
from multiprocessing import Pool

from pieChart import get_ascii_pie

NUMBER_OF_THREADS = 10

def get_parser() -> argparse.ArgumentParser:
    """
    Create a parser for the command line arguments.
    """
    parser = argparse.ArgumentParser(
                    prog='GitPie',
                    description='Create a pie chart of authors contributions to current lines of code in a git repository',)

    parser.add_argument('-v', '--verbose', help='Verbose output', action='store_true')
    parser.add_argument('-r', '--repo', help='Path to the git repository', default=None)
    parser.add_argument('-l', '--load', help='Load authors from file', default=None)
    parser.add_argument('-a', '--authors', help='File to write authors to', default=None)
    parser.add_argument('-s', '--size', help='Size of the pie chart', default=10)

    return parser

def get_repo_filenames(repo_path, verbose=False) -> list:
    """
    Get the list of files in the repository at the given path.
    :param repo_path: The path to the git repository
    :param verbose: Whether to print verbose output (default: False)
    :return: A list of files in the repository
    """
    if verbose:
        print('Getting files in the repository at {}'.format(repo_path))
    files = subprocess.check_output(['git', 'ls-files'], cwd=repo_path).splitlines()
    files = [file.decode('utf-8') for file in files]
    if verbose:
        print('Found {} files in the repository'.format(len(files)))
    return files

def extract_author(line: str) -> str:
    """ 
    Extract the author from a line of git blame output.
    This only works for commits in the 21st century. Behavior is undefined for commits before 2000.
    Also could have issues for authors with '(' or ' 20' in their name.
    :param line: A line of git blame output
    :return: The author of the line
    """
    try:
        return (line.split('(')[1]).split(' 20')[0].strip() # Only works for 21st century
    except:
        return None

def get_authors_for_file(repo_path, filename, verbose=False) -> dict:
    """
    Get number of lines of code contributed by each author for a given file.
    :param repo_path: The path to the git repository
    :param filename: The file to get authors for
    :param verbose: Whether to print verbose output (default: False)
    :return: A dictionary of authors and the number of lines contributed
    """
    try: 
        blame = subprocess.check_output(['git', 'blame', filename], cwd=repo_path).splitlines()
        blame = [line.decode('utf-8') for line in blame]
        authors = dict()
        for line in blame:
            author = extract_author(line)
            if author is None:
                continue
            if author not in authors:
                authors[author] = 1
            else:
                authors[author] += 1
    except Exception as e:
        print('Error getting authors for file {}. Skipping...'.format(filename))
        return None
    if verbose:
        print('Found {} authors for file {}'.format(len(authors), filename))
    return authors

def load_authors_from_file(file: str) -> dict:
    """
    Load authors from a file. File should be in the format:
    author1,count1
    author2,count2
    ...
    :param file: The file to load authors from
    :return: A dictionary of authors and the number of lines contributed
    """
    authors = dict()
    with open(file, 'r') as f:
        for line in f:
            try:
                author, count = line.strip().split(',')
                authors[author] = int(count)
            except:
                print('Error parsing line: {}'.format(line))
    return authors

def group_lowest_authors(data: list, threshold_percent: float) -> list:
    """
    Group authors with less than a certain percentage of the total lines into an 'Other' category.
    :param data: The data to group
    :param threshold_percent: The percentage of total lines below which to group authors
    :return: The grouped data
    """
    total = sum([value for _, value in data])
    threshold = total * threshold_percent
    other = 0
    new_data = []
    for author, value in data:
        if value < threshold:
            other += value
        else:
            new_data.append((author, value))
    new_data.append(('Other', other))
    return new_data

def main():
    """
    Main function for the script. See get_parser() for command line arguments
    """
    parser = get_parser()
    args = parser.parse_args()

    if args.repo is not None and args.load is not None:
        print('Cannot specify both a repository and a load file')
        return
    try:
        size = int(args.size)
    except:
        print('Size must be an integer')
        return

    authors = dict()
    if args.load is not None:
        authors = load_authors_from_file(args.load)
    elif args.repo is not None:
        repo_files = get_repo_filenames(args.repo, args.verbose)
        with Pool(NUMBER_OF_THREADS) as p:
            results = p.starmap(get_authors_for_file, [(args.repo, file, args.verbose) for file in repo_files])
            for result in results:
                if result is not None:
                    for author, value in result.items():
                        if author not in authors:
                            authors[author] = value
                        else:
                            authors[author] += value
    else:
        print('Must specify either a repository or a load file')
        return
    
    if args.authors is not None:
        with open(args.authors, 'w') as f:
            for key in authors.keys():
                f.write('{},{}\n'.format(key, authors[key]))

    authors = list(authors.items())
    authors.sort(key=lambda x: x[1], reverse=True)
    authors = group_lowest_authors(authors, 0.05)

    if args.verbose:
        print('Authors:')
        for author, value in authors:
            print('{}: {}'.format(author, value))
    
    
    output = get_ascii_pie(authors, size)
    print(output)

if __name__ == "__main__":
    main()
