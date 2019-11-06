.. _user-guide:

**********
User Guide
**********

This guide is indented as an informal introduction into basic concepts and features of apace. For a detailed
reference of its classes and functions, see :ref:`api-reference`.

The Data Model
==============
All data describing the structure and properties of the accelerator is
represented by different objects. This sections gives an brief overview of the most important classes.

.. _elements:

Element Classes
---------------

All basic components of the magnetic lattice like drift spaces, bending magnets and quadrupole are a subclass of an abstract
base class called :class:`Element`. All elements have a name (which should be unique), a length and an optional description.

You can create a new :class:`Drift` space with::

   drift = ap.Drift(name='Drift', length=2)

Check that the :code:`drift` is actually a subclass of :class:`Element`::

   >>> isinstance(drift, ap.Element)
   True

To create the more interresting :class:`Quad` object use::

   quad = ap.Quad(name='Quad', length=1, k1=1)

The attributes of elements can also be changed after they a created::

   >>> quad.k1
   1
   >>> quad.k1 = 0.8
   >>> quad.k1
   0.8

.. note::
   You can also set up an event listener to whenever an element gets changed, for more information see :ref:`signals`.

When using Python interactively you can get further information on a specific element with the builtin :func:`print` function::

   >>> print(quad)
   name          : Quad
   description   :
   parent_cells  : set()
   k1            : 0.8
   length        : 1
   length_changed: Signal
   value_changed : Signal

As you can see, the :class:`Quad` object has by default the :attr:`~Object.parent_cells` attribute, which we will
dicuss in the next subsection.

Cell class
--------------
The magnetic lattice of modern Particle accelerators is typically more complex than a single quadrupole. Therefore multiple elements can be arranged into a more complex structure using the :class:`Cell` class.

Creating a Double Bend Achromat
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As we already created a FODO structure in :ref:`quickstart`, let's create a
`Double Bend Achromat Lattice <https://en.wikipedia.org/wiki/Chasman%E2%80%93Green_lattice>`_ this time. In addition to
our :code:`drift` and :code:`quad` elements, we need a new :class:`Bend` object::

   bend = ap.Bend('Bend', length=1, angle=math.pi / 16)

Now we can create a DBA cell::

   dba_cell = ap.Cell('DBA Cell', [drift, bend, drift, quad, drift, bend, drift])

As you can see, it is possible for elements to occur multiple times within the same cell. Elements can even be in different cells at the same time. What is important to notice is, that all instances of the element (for example all instances :code:`drift` within the :code:`dba_cell`) correspond to the same underlying object.

You can easily check this by changing the length of the :code:`drift` and displaying the length of the :code:`dba_cell` before and afterwards::

   >>> dba_cell.length
   11
   >>> drift.length += 0.25
   >>> dba_cell.length
   12

As the :code:`drift` space appears four times within the :code:`dba_cell` its length increased four-fold.

Parent Cells
^^^^^^^^^^^^

You may have also noticed that length of the :code:`dba_cell` was updated automatically without you having to call any update function. This works because apace keeps track of all parent cells through the :attr:`~Object.parent_cells` attribute and informs all parents whenever the length of an element changes.

.. note::
    Apace only notifies the cell that it has to update its length value. The calculation of new length only happens when the attribute is accessed. This may be not that advantageous for a simple length calculation, but (apace uses this system for all its data) makes a difference for  more computational expensive properties. For more see :ref:`lazy_eval`.

Try to print the contents of :attr:`~Object.parent_cells` for the :code:`quad` object::

   >>> quad.parent_cells
   {Cell}

In contrast to the end of :ref:`elements` section, where it was empty, :code:`quad.parent_cells` now has one entry. Note that this is a Python :class:`set`, so it cannot to contain duplicates in case that an element appears multiple times within the same cell. The set gets updated whenever an element gets added or removed from a cell.

It is also possible to create a cell out of cells. For example you could create a DBA ring using the already existing :code:`dba_cell`::

   dba_ring = ap.Cell('DBA Ring', [dba_cell] * 16)

The :code:`dba_ring` should now be listed as a parent of the :code:`dba_cell`::

   >>> dba_cell.parent_cells
   {DBA Ring}

Its length should be 16 times the length of the :code:`dba_cell`::

   >>> dba_ring.length
   192.0

The Object Tree
^^^^^^^^^^^^^^^

The structure which defines the order of elements in our DBA ring can be thought of as a `Tree <https://en.wikipedia.org/wiki/Tree_structure>`_, where :code:`dba_ring` is the root, the :code:`dba_cell` objects are the nodes and the :code:`bend`, :code:`drift` and :code:`quad` elements are the leafes. The attribute which stores the arrangement of objects within a cell is therefore called :attr:`~Cell.tree`. Try to output the tree for the :code:`dba_ring` and :code:`dba_cell` objects::

   >>> dba_ring.tree
   [DBA Cell, DBA Cell, DBA Cell, DBA Cell, DBA Cell, DBA Cell, DBA Cell, DBA Cell, DBA Cell, DBA Cell, DBA Cell, DBA Cell, DBA Cell, DBA Cell, DBA Cell, DBA Cell]
   >>> dba_cell.tree
   [Drift, Bend, Drift, Quad, Drift, Bend, Drift]


This can be also visualized by calling the :meth:`Cell.print_tree` method::

   >>> dba_ring.print_tree()
   DBA Ring
   ├─── DBA Cell
   │   ├─── Drift
   │   ├─── Bend
   │   ├─── Drift
   │   ├─── Quad
   │   ├─── Drift
   │   ├─── Bend
   │   └─── Drift
   # ... 14 times more ...
   └─── DBA Cell
       ├─── Drift
       ├─── Bend
       ├─── Drift
       ├─── Quad
       ├─── Drift
       ├─── Bend
       └─── Drift

As a nested structure is not always convenient to work with, there are three other representations of :attr:`~Cell.tree` (internally called :code:`tree_properties`):

#. The :attr:`Cell.lattice` attribute

   To loop over the exact arrangement of objects there is :attr:`Cell.lattice` attribute, which is a list of :class:`~Element` objects. It can be thought of a flattened version of the tree. The :attr:`~Cell.lattice` attribute can be used in regular Python :code:`for ... in` loops::

      >>> sum(element.length for element in dba_ring.lattice)
      192

   As the :code:`dba_cell` does not contain any other cells, the :attr:`~Cell.lattice` and :attr:`~Cell.tree` attributes should be equal::

      >>> dba_cell.tree == dba_cell.lattice
      True

   On the other hand, the :attr:`~Cell.lattice` attribute of the :code:`dba_ring` should look different then its :attr:`~Cell.tree`::

      >>> dba_ring.tree
      [Drift, Bend, Drift, Quad, Drift, Bend, Drift, Drift, Bend, Drift, Quad, Drift, Bend, Drift, Drift, Bend, Drift, Quad, Drift, Bend, Drift, Drift, Bend, Drift, Quad, Drift, Bend, Drift, Drift, Bend, Drift, Quad, Drift, Bend, Drift, Drift, Bend, Drift, Quad, Drift, Bend, Drift, Drift, Bend, Drift, Quad, Drift, Bend, Drift, Drift, Bend, Drift, Quad, Drift, Bend, Drift, Drift, Bend, Drift, Quad, Drift, Bend, Drift, Drift, Bend, Drift, Quad, Drift, Bend, Drift, Drift, Bend, Drift, Quad, Drift, Bend, Drift, Drift, Bend, Drift, Quad, Drift, Bend, Drift, Drift, Bend, Drift, Quad, Drift, Bend, Drift, Drift, Bend, Drift, Quad, Drift, Bend, Drift, Drift, Bend, Drift, Quad, Drift, Bend, Drift, Drift, Bend, Drift, Quad, Drift, Bend, Drift]


#. The :attr:`Cell.elements` attribute

   If the elements are loaded from a lattice file, you do no have individual Python variables to access them. For this purpose you can use the :attr:`Cell.elements` attribute, which is a key value pair of :attr:`Element.name` and :class:`Element` objects. You can access a specific element of a cell with::

      >>> drift = dba_ring['Drift']
      >>> drift.length
      2.25

   To loop over all elements in no specific order use :func:`Cell.elements.values` ::

      >>> for element in dba_ring.elements.values():
      >>>   print(element.name, element.length)
      Drift 2.25
      Bend 1
      Quad 1

   .. note::

      In contray to :attr:`Cell.lattice` elements to not appear multiple times in :attr:`Cell.elements.values()`. It can be thought of as a :class:`set` of :attr:`~Cell.lattice`.


#. The :attr:`Cell.cells` attribute

    Similar to the :attr:`Cell.elements` attribute but for cells. Contains all cells within a given cell, including grandchilrden, great grandchildren, etc.
    This should be empty for the :code:`dba_cell` as it does not contain any other cells::
      >>> dba_cell.cells
      {}

Adding and Removing Objects
---------------------------

The :attr:`~Cell.tree` of objects can also be altered after the cell was created. Use :meth:`Cell.add` to add objects to the tree::

   >>> dba_cell.add(drift)
   >>> dba_cell.tree
   [Drift, Bend, Drift, Quad, Drift, Bend, Drift, Drift]

Remove objects from the :attr:`~Cell.tree` with :meth:`Cell.remove`::

   >>> dba_cell.remove(-1)
   >>> dba_cell.tree
   [Drift, Bend, Drift, Quad, Drift, Bend, Drift]

The Twiss object
----------------


Container object of the Twiss parameter

The Tracking object
-------------------

.. _signals:

Signals and Events
==================

Here comes text


.. _lazy_eval:

Lazy Evaluation
---------------

Lattice File Format
===================
The layout and order of elements within an accelerator is usually stored in a so-called "lattice file". There are a variety of different lattice files and different attempts to unify them:

* MAD and elegant have relatively human readable lattice files but are difficult to parse and also not commonly used in other areas.

* The Accelerator Markup Language (AML) is based on XML, which is partical to describe the hierarchical data structure of cells and elements within an accelerator and can be parsed by different languages. XML's main drawback is that it is fairly verbose, hence less human readable and has become less common recently.

apace tries to get the best out of both worlds and uses a JSON based lattice file. JSON is able to describe complex data structures, has a simple syntax and is available in all common programming language.

apace lattice file for a simple fodo ring:

.. literalinclude:: ../examples/lattices/fodo_ring.json
  :language: JSON



