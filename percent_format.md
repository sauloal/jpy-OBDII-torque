https://towardsdatascience.com/jupyter-notebooks-as-light-percent-or-sphinx-scripts-efca8bc3aa44

#~/.jupyter/jupyter_notebook_config.py

c.NotebookApp.contents_manager_class="jupytext.TextFileContentsManager"

pip install --upgrade jupytext

# metadata
"jupytext": {
   "formats": "ipynb,py:percent"
  },

# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.1'
#       jupytext_version: 0.8.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
#   language_info:
#     codemirror_mode:
#       name: ipython
#       version: 3
#     file_extension: .py
#     mimetype: text/x-python
#     name: python
#     nbconvert_exporter: python
#     pygments_lexer: ipython3
#     version: 3.6.6
# ---


# Convert light.py to percent.py
jupytext --from py:light --to py:percent --output percent.py light.py

# In place conversion! Handle with care.
jupytext --from py:light --to py:percent notebook.py