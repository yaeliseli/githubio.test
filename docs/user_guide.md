User Guide
==========

Start DHTK
----------

### Loading DHTK

As a Python module, DHTK can be accessed from any Python console or
environment by
[importing](https://docs.python.org/3/reference/import.html?highlight=import)
it as normally.

### Setting up Configurations

The first step to use DHTK is to set the configurations to use by
calling **dhtk.start()**

This function instantiates DHTK's settings manager class, which searches
for the user's saved settings. It automatically prints all current
settings for the user's information.

DHTK contains a number of options to help users start up faster and
automatically, most of which have a default value. The settings to pay
more attention to are the following:


- *[wd]*: DHTK uses the user' home directory to set up its working
  directory. This can be modified if another directory would be more
  suitable.
- *[dataset]*: DHTK is a modular package to which extensions can be
  easily added. This setting determines which of the available
  extension modules DHTK should load.
- *[endpoint]*: To use a remote (on-line) endpoint, it can be done by adding the URL (link) to the
  remote endpoint. To use a local  server endpoint for querying pre-processed datasets use *[storage]* configuration.
- *[storage]*:  To use a remote (on-line) endpoint, it can be done by adding the URL (link) to the
  remote endpoint. To use a remote  server endpoint for querying pre-processed datasets use *[endpoint]* configuration.

---
 **note**

 Dataset does not have a default value and must be set **the first
 time** a user runs DHTK.
---
### Modifying configurations

Configurations can be *set directly* by passing their values as keyword
arguments to the `dhtk.start()` function.


DHTK data sources
---------------

Using the settings, DHTK will determine which SPARQL endpoint to connect
and which extension module to load. 

Currently, DHTK includes the following extensions:

-   [Project Gutenberg](#gutenberg)
-   [Auchinkleck manuscript](#auchinleck)

### Gutenberg

DHTK's Gutenberg extension dataset allows the user to easily query
[Gutenberg.org](http://gutenberg.org/) for **books, authors, bookshelves
and subjects**, retrieving all the available information as a DHTK
Corpus.

DHTK provides a simple dictionary-like syntax to search Guntenberg's
dataset using the method **.get()**. This method allows the user to
easily query the entire dataset using a single interface with only 3
keyword arguments:

-   [*what*] to search for.
-   [*name*] of what is being searched. If no name is provided, all
    available options are retrieved.
-   [*add*] to corpus or just search results?

<br>
#### Exploring Data

To **search** Gutenberg's data, set *add=False*. For such queries, DHTK
Gutenberg's module returns a dictionary of books or authors matching the
query.

---
 **note**

 *add=False* is the default value, so this argument can be simply
 ignored by the user in such cases.
---
****Searching for a bookshelf****

To check which [bookshelves](http://www.gutenberg.org/ebooks/bookshelf/)
are available in DHTK's Gutenberg, set *what="shelf"* and *name="all"*.
---
 **note**

 *name="all"* is the default value, so this argument may be simply
 ignored by the user.
---
To search for books available for a bookshelf, the name, or part of the
name, of an available bookshelf is passed to the *name* argument. For
example, to search all books in "Science Fiction" bookshelves:

The list of bookshelves matching the query are stored as the dictionary
keys for easy access:

The information for individual bookshelves can be easily retrieved using
the dictionary key. This strutcture makes it easy to perform all types
of regular Python operations. For example, to identify all books that
are simultaneously found on the bookshelves "Precursors of Science
Fiction" and "Science Fiction by Women":

****Searching for a subject****

Gutenberg [subjects](http://www.gutenberg.org/ebooks/subjects/search/)
can be searched using *what="subject"*. Subject names are structured
hierarchically, making it possible to define the granularity of such
queries. Each hierarchy is separated by -- *(e.g. Subject -- Sub-subject
-- Sub-sub-subject)*

****Searching for a book****

Gutenberg books can be searched using the *what="book"* argument. This
will return a dictionary of books containing the text passed as *name*.
To avoid long names, the dictionary keys returned are truncated at 20
characters.

****Searching for an author****

Gutenberg books can be searched using the *what="author"* argument.

#### Check metadata

DHTK Guntenberg's module uses books and authors objects to store all the
relevant information retrieved. These objects can be accessed directly
from the dictionaries obtained while searching as described above.
---
 **note**

 The book and author objects are not returned when searching for
 bookshelves and subjects. These queries are considered more
 exploratory and instantiating all objects would be less efficient in
 respect to both performance and memory.
---
****Get book information****

Retrieving metadata is simple as all Gutenberg objects have the
**.print\_info()** method:

****Get author information****

Author objects are retrieved with author searches as described above.
However, book objects also contain the author information as attribute.
Because of this, there are two ways to access an author object:

Accessing the author's information can be done as easily as for books,
using the **.print\_info()** method:

****Get book text****

The original text for a Gutenberg book can also be accessed if required,
using the GutenbergBook method **.original\_text()**.

#### Saving results

To add the retrieved book to a DHTK Corpus use *add=True*. A list of
GutenbergBook objects is created containing all the textual data and
metadata retrieved from [Guntenberg.org](http://www.gutenberg.org/).
---
 **note**

 Each query that uses *add=True* will add the resulting books to the
 same module object. This means that a new module needs to be
 instantiated with **.get\_module()** function for each different
 corpus
---
****Make a Corpus****

****Retrieve books****

Individual books can be retrieved from a Gutenberg Corpus using the
**.books()** method and passing a book name to the *get* argument.

Passing the value *get="all"* will return a dictionary of books added to
the corpus.

****Modifying Corpus****

As seem in the "Get book information" above, the book *Frankenstein; Or,
The Modern Prometheus* with ID *<http://www.gutenberg.org/ebooks/84>*
has "an improved edition". To remove the old edition, the argument
*remove=True* can be passed to the method **.books()**.

Before saving the Corpus to disk, it is important to review the Corpus
descriptions, particularly the corpus name, which is used as the
directory where the books will be stored. This can be done simply by
passing the *name* and *description* arguments to the **.corpus()**
method used above.

****Save Corpus****

When all the information as been added to a corpus, it can be easily
saved to disk using the **.save()** method.
