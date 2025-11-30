<!--TOC using https://github.com/ekalinin/github-markdown-toc-->
<!--ts-->
   * [Pandas for Everyone](#pandas-for-everyone)
   * [Setup](#setup)
      * [Install seaborn for plotting](#install-seaborn-for-plotting)
      * [Install all the packages used in the book](#install-all-the-packages-used-in-the-book)
         * [(Optional) Create a Virtual Environment](#optional-create-a-virtual-environment)
         * [Install the packages](#install-the-packages)

<!-- Added by: dchen, at: 2018-04-05T23:01-04:00 -->

<!--te-->

# Pandas for Everyone

If you have gone through the book, an
[Amazon review](https://www.amazon.com/Pandas-Everyone-Analysis-Addison-Wesley-Analytics/dp/0134546938/ref=sr_1_1?ie=UTF8&qid=1522984377&sr=8-1&keywords=pandas+for+everyone)
would be much appreciated!
My mom would too :)

# Setup


## Install seaborn for plotting

`conda install seaborn`

## Install all the packages used in the book
There is an error in the preface of the book for installing packages.
I am leaving this section here in the README to have an updated list of packages and installation instructions

### (Optional) Create a Virtual Environment

You can choose to create a virtual envirionment for the packages used in the book,
so it doesn't clash with other packages you plan to use later on.

```bash
# create a virtual environment named "book" using python 3.6
conda create -n book python=3.6

# activate the environment
# so all installed packages will go in there and not mess up your base python environment
source activate book
```

### Install the packages

Whether you decited to create a virtual environment or not, you can install the packages with the below commands.
If you did use virtual environments, remember to `source activate book` before you follow along with the book
so the packages you installed can be loaded.

```bash
conda install pandas xlwt openpyxl seaborn numpy ipython jupyter statsmodels scikit-learn regex wget odo numba
conda install -c conda-forge pweave # you don't really need this package, it was used to build and create the book
conda install -c conda-forge feather-format
pip install lifelines pandas-datareader
```


