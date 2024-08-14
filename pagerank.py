import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    probability_distribution = dict()

    if len(corpus[page]) == 0:
        for key in corpus:
            probability_distribution[key] = (1 - damping_factor) / len(corpus)

    else:
        values = set()
        for key in corpus:
            if key == page:
                values = corpus[key]

        # Probability for a link in page
        value_1 = damping_factor / len(values)

        # Probability for every page in corpus
        value_2 = (1 - damping_factor) / len(corpus)

        for key in corpus:
            if key in values:
                probability_distribution[key] = value_1 + value_2
            else:
                probability_distribution[key] = value_2

    return probability_distribution


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    page_rank = dict()
    sample_list = []
    pages = list(corpus.keys())
    sample = None

    for i in range(n):

        if sample is None:
            sample = random.choice(pages)
            sample_list.append(sample)
        else:
            page_sequence = list(transition_model(corpus, sample, damping_factor).keys())
            page_weights = list(transition_model(corpus, sample, damping_factor).values())
            sample = random.choices(population=page_sequence, weights=page_weights, k=1)[0]
            sample_list.append(sample)

    for key in corpus:
        count = sample_list.count(key)
        page_rank[key] = count / n

    return page_rank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    PR = dict()
    links = set()
    for page in corpus:
        if len(corpus[page]) == 0:
            for add_link in corpus:
               links.add(add_link)
            corpus[page] = links

    for p in corpus:
        PR[p] = 1 / len(corpus)

    while True:
        counter = 0
        current = PR.copy()
        for p in corpus:
            recursive_value = 0
            for link in corpus:
                if p in corpus[link]:
                    recursive_value += current[link] / len(corpus[link])

            value = (1 - damping_factor) / len(corpus)
            PR[p] = value + damping_factor * recursive_value
            if abs(current[p] - PR[p]) < 0.001:
                counter += 1

        if counter == len(corpus):
            break

    return current


if __name__ == "__main__":
    main()
