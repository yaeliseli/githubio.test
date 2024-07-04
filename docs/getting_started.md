Getting Started
==============

Start with DHTK
---------------

As a Python module, DHTK can be accessed from any Python console or
environment by
[importing](https://docs.python.org/3/reference/import.html?highlight=import)
it as normally.

### Import dhtk

```python
import dhtk
 # ###################################################
 # Welcome to the Digital Humanities ToolKit,
 # the  user - friendly Python API for
 # Digital Humanities research.
 #
 # For more information, please visit DHTK 's website:
 # [https://dhtk.unil.ch/]
 # ####################################################
``` 
DHTK contains a number of options to help users start up faster and
automatically, most of which have a default value. The settings to pay
more attention to are the following:

- *[wd]*: DHTK uses the user' home directory to set up its working
    directory. This can be modified if another directory would be more
    suitable.
- *[dataset]*: DHTK is a modular package to which extensions can be easily added. 
    This setting determines the available
    extension modules that DHTK should load.
- *[endpoint]*: To use a remote (on-line) endpoint, it can be done by adding the URL (link) to the
    remote endpoint. To use a local  server endpoint for querying pre-processed datasets use *[storage]* configuration.
- *[storage]*:  To use a remote (on-line) endpoint, it can be done by adding the URL (link) to the
    remote endpoint. To use a remote  server endpoint for querying pre-processed datasets use *[endpoint]* configuration.

DHTK is flexible and can accept several input formats. Hereunder, there are several working examples:

### Set DHTK configuration file
```python
import dhtk
d  = dhtk.start("WD", config={"gutenberg": {"storage":  "docker"}, "auchinleck": {"storage": "docker" }})

d = dhtk.start("WD", config={"gutenberg":{'triplestore' : {"storage":  "docker"}}})

d =dhtk.start("WD", data_source="gutenberg", storage="docker")

d = dhtk.start("WD", data_sources=["gutenberg", "auchinleck"], storage="docker")

d = dhtk.start("WD", gutenberg={"storage": "docker"}, auchinleck={"endpoint": "http://localhost:3031/ds/sparql" } )

```

### Load the module
Modules are automatically loaded using the *dhtk.start()* function. 
In this guided example, we will illustrate using the original Gutenberg DHTK data source. 
This dataset allows the user to easily query [https://www.gutenberg.org/](https://www.gutenberg.org/) for books, authors, bookshelves and subjects, retrieving all the available information as a DHTK Corpus.

### Access the data
Authors are searched using the *what="author"* argument. This will return a Python list containing all authors. To access a particular author, users must pass the author's name to the *name* argument.
```python
authors = gutenberg.get(what="author", name="Shelley")
authors
# {'Percy Bysshe Shelley': <Author: Shelley, Percy (http://www.gutenberg.org/2009/agents/1529>),
# 'Henry Charles Shelley': <Author: Shelley, Henry (http://www.gutenberg.org/2009/agents/2162>),
# 'Mary Wollstonecraft Shelley': <Author: Shelley, Mary (http://www.gutenberg.org/2009/agents/61>)}
```
then to access to *Mary Wollstonecraft Shelley* GutenbergAuthor object.
```python
>> authors['Mary Wollstonecraft Shelley']
# <Author: Shelley, Mary (http://www.gutenberg.org/2009/agents/61>)
```
Similarly, Books are searched using the *what="book"* argument. This will return a list containing all books.
```python
books = gutenberg.get(what="books", name="Frankenstein")
books
# {'Frankenstein; Or, Th (41445)': <GutenbergBook: Mary Wollstonecraft Shelley - Frankenstein; Or, The Modern Prometheus gutenberg_id: 41445>,
# 'Frankenstein; Or, Th (42324)': <GutenbergBook: Mary Wollstonecraft Shelley - Frankenstein; Or, The Modern Prometheus gutenberg_id: 42324>,
# 'Frankenstein; Or, Th (84)': <GutenbergBook: Mary Wollstonecraft Shelley - Frankenstein; Or, The Modern Prometheus gutenberg_id: 84>}
books["Frankenstein; Or, Th (84)"]
# <GutenbergBook: Mary Wollstonecraft Shelley - Frankenstein; Or, The Modern Prometheus gutenberg_id: 84>
```
and retrieve a specific book.
```python
book = books['Frankenstein; Or, Th (84)']
```
DHTK allows users to get access to metadata on a given book (or author) built on information collected in Project Gutenberg.

```python
book.print_info()
# Title       : Frankenstein; Or, The Modern Prometheus
# Author      : Mary Wollstonecraft Shelley
# Metadata    :
#     - subject     :
#             - Horror tales
#             - Scientists--Fiction
#             - Gothic fiction
#             - Frankenstein, Victor (Fictitious character)--Fiction
#             - Monsters--Fiction
#             - Frankenstein's monster (Fictitious character)--Fiction
#             - Science fiction
#     - bookshelf   :
#             - Precursors of Science Fiction
#             - Science Fiction by Women
#             - Movie Books
#             - Gothic Fiction
#     - gutenberg_id: http://www.gutenberg.org/ebooks/84
#     - gutenberg_type: http://www.gutenberg.org/2009/pgterms/ebook
#     - gutenberg_downloads:        34221
#     - gutenberg_publisher: Project Gutenberg
#     - gutenberg_hasFormat:
#             - http://www.gutenberg.org/files/84/84-h.zip
#             - http://www.gutenberg.org/files/84/84-0.txt
#             - http://www.gutenberg.org/ebooks/84.kindle.images
#             - http://www.gutenberg.org/ebooks/84.epub.images
#             - http://www.gutenberg.org/ebooks/84.epub.noimages
#             - http://www.gutenberg.org/cache/epub/84/pg84.cover.medium.jpg
#             - http://www.gutenberg.org/ebooks/84.rdf
#             - http://www.gutenberg.org/files/84/84-h/84-h.htm
#             - http://www.gutenberg.org/cache/epub/84/pg84.cover.small.jpg
#             - http://www.gutenberg.org/files/84/84-0.zip
#             - http://www.gutenberg.org/ebooks/84.kindle.noimages
#     - gutenberg_language:           en
#     - gutenberg_rights: Public domain in the USA.
#     - gutenberg_title: Frankenstein; Or, The Modern Prometheus
#     - gutenberg_issued:   1993-10-01
#     - gutenberg_creator: http://www.gutenberg.org/2009/agents/61
#     - gutenberg_license: http://www.gutenberg.org/license
#     - gutenberg_description: There is an improved edition of this title, eBook #42324
metadata = book.get_metadata()
```

***to know more***`

please refer to the [user guide page](user_guide.md)