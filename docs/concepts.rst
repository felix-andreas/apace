========
Concepts
========


The Magnetic Lattice
====================

Elements
--------

Cells
-----

The MainCell
------------

apace Lattice File
==================
The layout and order of elements within an accelerator is usually stored in a so-called "lattice file". There are a variety of different lattice files and different attempts to unify them:

- MAD and elegant have relativly human readable lattice files but are difficult to parse and also not commonly used in other areas.

- The Accelerator Markup Language (AML) is based on XML, which is partical to describe the hierarchical data structure of cells and elements within an accelerator and can be parsed by different languages. XML's main drawback is that it is fairly verbose, hence less human readable and has become less common recently.

apace tries to get the best out of both worlds and uses a JSON based lattice file. JSON is able to describe complex data structures, has a simple syntax and is available in all common programming language.

apace lattice file for a simple fodo ring:

.. literalinclude:: ../examples/lattices/fodo_ring.json
  :language: JSON


The Twiss object
================
