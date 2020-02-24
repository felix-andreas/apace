.. _user-guide:

**********
User Guide
**********

This guide is indented as an informal introduction into basic concepts and features of apace. For a detailed
reference of its classes and functions, see :ref:`api-reference`.

All data describing the structure and properties of the accelerator is
represented by different objects. This sections gives an brief overview of the most important classes.

.. _elements:

Element Classes
===============

All basic components of the magnetic lattice like drift spaces, bending magnets and quadrupole are a subclass of an abstract
base class called :class:`Element`. All elements have a name (which should be unique), a length and an optional description.

You can create a new :class:`Drift` space with::

   drift = ap.Drift(name='Drift', length=2)

Check that the :code:`drift` is actually a subclass of :class:`Element`::

   >>> isinstance(drift, ap.Element)
   True

To create the more interresting :class:`Quadrupole` object use::

   quad = ap.Quadrupole(name='Quadrupole', length=1, k1=1)

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
   name          : Quadrupole
   description   :
   parent_lattices  : set()
   k1            : 0.8
   length        : 1
   length_changed: Signal
   value_changed : Signal

As you can see, the :class:`Quadrupole` object has by default also the :attr:`~Base.parent_lattices` attribute, which we will
discuss in the next subsection.

Lattice class
=============
The magnetic lattice of modern Particle accelerators is typically more complex than a single quadrupole. Therefore multiple elements can be arranged into a more complex structure using the :class:`Lattice` class.

Creating a Double Dipole Achromat
---------------------------------

As we already created a FODO structure in :ref:`quickstart`, let's create a
`Double Dipole Achromat Lattice <https://wikipedia.org/wiki/Chasman%E2%80%93Green_lattice>`_ this time. In addition to
our :code:`drift` and :code:`quad` elements, we need a new :class:`Dipole` object::

   bend = ap.Dipole('Dipole', length=1, angle=math.pi / 16)

Now we can create a DBA lattice::

   dba_cell = ap.Lattice('DBA_CELL', [drift, bend, drift, quad, drift, bend, drift])

As you can see, it is possible for elements to occur multiple times within the same lattice. Elements can even be in different lattices at the same time. What is important to note is, that elements which appear within a lattice multiple times (e.g. all instances of :code:`drift` within the :code:`dba_cell`) correspond to the same underlying object.

You can easily check this by changing the length of the :code:`drift` and displaying the length of the :code:`dba_cell` before and afterwards::

   >>> dba_cell.length
   11
   >>> drift.length += 0.25
   >>> dba_cell.length
   12

As the :code:`drift` space appears four times within the :code:`dba_cell` its length increased four-fold.

.. _parent-lattices:

Parent lattices
---------------

You may have also noticed that length of the :code:`dba_cell` was updated automatically without you having to call any update function. This works because apace keeps track of all parent lattices through the :attr:`~Base.parent_lattices` attribute and informs all parents whenever the length of an element changes.

.. note::
    Apace only notifies the lattice that it has to update its length value. The calculation of new length only happens when the attribute is accessed. This may be not that advantageous for a simple length calculation, but (apace uses this system for all its data) makes a difference for  more computational expensive properties. For more see :ref:`lazy_eval`.

Try to print the contents of :attr:`~Base.parent_lattices` for the :code:`quad` object::

   >>> quad.parent_lattices
   {Lattice}

In contrast to the end of :ref:`elements` section, where it was empty, :code:`quad.parent_latticess` now has one entry. Note that this is a Python :class:`set`, so it cannot to contain duplicates in case that an element appears multiple times within the same lattice. The set gets updated whenever an element gets added or removed from a :class:`Lattice`.

It is also possible to create a lattice out of lattices. For example you could create a DBA ring using the already existing :code:`dba_cell`::

   dba_ring = ap.Lattice('DBA_RING', [dba_cell] * 16)

The :code:`dba_ring` should now be listed as a parent of the :code:`dba_cell`::

   >>> dba_cell.parent_lattices
   {DBA_RING}

Its length should be 16 times the length of the :code:`dba_cell`::

   >>> dba_ring.length
   192.0

The Base Tree
---------------

The structure which defines the order of elements in our DBA ring can be thought of as a `Tree <https://wikipedia.org/wiki/Tree_structure>`_, where :code:`dba_ring` is the root, the :code:`dba_cell` objects are the nodes and the :code:`bend`, :code:`drift` and :code:`quad` elements are the leafes. The attribute which stores the order of objects within a lattice is therefore called :attr:`~Lattice.tree`. Try to output the tree for the :code:`dba_ring` and :code:`dba_cell` objects::

   >>> dba_ring.tree
   [DBA_CELL, DBA_CELL, DBA_CELL, DBA_CELL, DBA_CELL, DBA_CELL, DBA_CELL, DBA_CELL, DBA_CELL, DBA_CELL, DBA_CELL, DBA_CELL, DBA_CELL, DBA_CELL, DBA_CELL, DBA_CELL]
   >>> dba_cell.tree
   [Drift, Dipole, Drift, Quadrupole, Drift, Dipole, Drift]


This can be also visualized by calling the :meth:`Lattice.print_tree` method::

   >>> dba_ring.print_tree()
   DBA_RING
   ├─── DBA_CELL
   │   ├─── Drift
   │   ├─── Dipole
   │   ├─── Drift
   │   ├─── Quadrupole
   │   ├─── Drift
   │   ├─── Dipole
   │   └─── Drift
   # ... 14 times more ...
   └─── DBA_CELL
       ├─── Drift
       ├─── Dipole
       ├─── Drift
       ├─── Quadrupole
       ├─── Drift
       ├─── Dipole
       └─── Drift

As a nested structure is not always convenient to work with, there are three other representations of :attr:`~Lattice.tree` (internally called :code:`tree_properties`):

#. The :attr:`~Lattice.lattice` attribute

   To loop over the exact arrangement of objects there is the :attr:`Lattice.lattice` attribute, which is a list of :class:`~Element` objects. It can be thought of a flattened version of the tree. The :attr:`~Lattice.lattice` attribute can be used in regular Python :code:`for ... in` loops::

      >>> sum(element.length for element in dba_ring.lattice)
      192

   As the :code:`dba_cell` does not contain any other lattices, the :attr:`~Lattice.lattice` and :attr:`~Lattice.tree` attributes should be equal::

      >>> dba_cell.tree == dba_cell.arrangement
      True

   On the other hand, the :attr:`~Lattice.lattice` attribute of the :code:`dba_ring` should look different then its :attr:`~Lattice.tree`::

      >>> dba_ring.arrangement
      [Drift, Dipole, Drift, Quadrupole, Drift, Dipole, Drift, Drift, Dipole, Drift, Quadrupole, Drift, Dipole, Drift, Drift, Dipole, Drift, Quadrupole, Drift, Dipole, Drift, Drift, Dipole, Drift, Quadrupole, Drift, Dipole, Drift, Drift, Dipole, Drift, Quadrupole, Drift, Dipole, Drift, Drift, Dipole, Drift, Quadrupole, Drift, Dipole, Drift, Drift, Dipole, Drift, Quadrupole, Drift, Dipole, Drift, Drift, Dipole, Drift, Quadrupole, Drift, Dipole, Drift, Drift, Dipole, Drift, Quadrupole, Drift, Dipole, Drift, Drift, Dipole, Drift, Quadrupole, Drift, Dipole, Drift, Drift, Dipole, Drift, Quadrupole, Drift, Dipole, Drift, Drift, Dipole, Drift, Quadrupole, Drift, Dipole, Drift, Drift, Dipole, Drift, Quadrupole, Drift, Dipole, Drift, Drift, Dipole, Drift, Quadrupole, Drift, Dipole, Drift, Drift, Dipole, Drift, Quadrupole, Drift, Dipole, Drift, Drift, Dipole, Drift, Quadrupole, Drift, Dipole, Drift]


#. The :attr:`~Lattice.elements` attribute

   If the elements are loaded from a lattice file, you do no have individual Python variables to access them. For this purpose you can use the :attr:`Lattice.elements` attribute, which is a key value pair of :attr:`Element.name` and :class:`Element` objects. You can access a specific element of a lattices with::

      >>> drift = dba_ring['Drift']
      >>> drift.length
      2.25

   To loop over all elements in no specific order use :func:`Lattice.elements.values` ::

      >>> for element in dba_ring.elements.values():
      >>>   print(element.name, element.length)
      Drift 2.25
      Dipole 1
      Quadrupole 1

   .. note::

      In contrary to :attr:`~Lattice.lattice` elements to not appear multiple times in :attr:`elements.values()`. It can be thought of as a :class:`set` of :attr:`~Lattice.lattice`.


#. The :attr:`~Lattice.sub_lattices` attribute

    This attribute is equivalent to the :attr:`~Lattice.elements` attribute but for lattices. It contains all lattices within a given lattice, including grandchildren, great grandchildren, etc.
    The :attr:`~Lattice.sub_lattices` attribute should be empty for the :code:`dba_cell` as it does not contain any other lattices::

      >>> dba_cell.sub_lattices
      {}

Adding and Removing Objects
---------------------------

As adding and removing objects from the :attr:`~Lattice.tree` significantly increased the
code complextetiy, it was decided that :attr:`~Lattice.tree` cannont be altered after the
:class:`Lattice` was created. If you needed to add/remove an object just create a new
:class:`Lattice` object or initially add an :class:`Element` with length zero, which can
be altered when needed.

Load and Save Lattice Files
---------------------------
lattices can also be imported from a lattice file. This can be done using the :func:`Lattice.from_file` method::

   lattice = ap.Lattice.from_file('/path/to/file')

Individual elements and sub-lattices can be accessed through the :attr:`~Lattice.elements` and :attr:`~Lattice.sub_lattices`, respectively::

   bend = lattice.elements['bend']
   sub_cell = lattice.sub_lattices['sub_cell']

A given lattice can be saved to a lattice file using the :func:`save_lattice` function::

   ap.Lattice.from_file(lattice, '/path/to/file')

The Twiss class
===============

The :class:`Twiss` class acts as container object for the Twiss parameter. Create a new :class:`Twiss` object for our DBA lattice::

   twiss = ap.Twiss(dba_ring)

The orbit position, horizontal beta and dispersion functions can be accessed through the :attr:`~Twiss.s`, :attr:`~Twiss.beta_x` and :attr:`~Twiss.eta_x` attributes, respectively::

   beta_x = twiss.beta_x
   s = twiss.s
   eta_x = twiss.beta_x

These are simple :class:`numpy.ndarray` objects and can simply plotted using :mod:`matplotlib`::

   import matplotlib.pyplot as plt
   plt.plot(s, beta_x, s, eta_x)

The tunes and betatron phase are available via :attr:`~Twiss.tune_x` and :attr:`~Twiss.psi_x`. To view the complete list of all attributes click 👉 :class:`Twiss` 👈.


The Tracking class
==================

Similar to the :class:`Twiss` class the :class:`Tracking` class acts as container for the tracking data. Before creating a new :class:`Tracking` object we need to create an initial particle distribution::

    n_particles = 100
    dist = create_particle_dist(n_particles, x_dist='uniform', x_width=0.001)

Now a :class:`Tracking` object for :code:`dba_ring` can be created with::

   track = ap.Tracking(dba_ring, dist, n_turns=2)

Now one could either plot horizontal particle trajectory::

   plt.plot(track.s, track.x)

Or, picture the particle movement within the horizontal phase space::

   plt.plot(track.x, track.x_dds)

Lattice File Format
===================
The layout and order of elements within an accelerator is usually stored in a so-called "lattice file". There are a variety of different lattice files and different attempts to unify them:

* MAD and elegant have relatively human readable lattice files but are difficult to parse and also not commonly used in other areas.

* The Accelerator Markup Language (AML) is based on XML, which is practical to describe the hierarchical data structure elements within an accelerator lattice, and can be parsed by different languages. XML's main drawback is that it is fairly verbose, hence less human readable and has become less common recently.

apace tries to get the best out of both worlds and uses a JSON based lattice file. JSON is able to describe complex data structures, has a simple syntax and is available in all common programming language.

apace lattice file for a simple fodo ring:

.. literalinclude:: ../examples/lattices/fodo_ring.json
  :language: JSON


Implementation Details
======================

.. _signals:

Signals and Events
------------------

As we have already seen in the :ref:`parent-lattices` section, the :attr:`~Lattice.length` of of a :class:`Lattice` gets updated whenever the length of one of its :class:`Element` objects changes. The same happens for the transfer matrices of  the :class:`Twiss` object. This is not only convenient - as one does not have to call an :func:`update` function every time an attribute changes - but is also more efficient, because apace has internal knowledge about which elements have changed and can accordingly only update the transfer matrices which have actually changed.


This is achieved by a so called `Observer Pattern <https://wikipedia.org/wiki/Observer_pattern>`_, where an **subject** emits an **event** to all its **observers**  whenever its state changes.

These events are implemented by the :class:`Signal` class. A callback can be connected to a given :class:`Signal` through the :meth:`~Signal.connect` method. Calling an instance of the :class:`Signal` will have the same effect as calling all connected callbacks.

**Example:** Each :class:`Element` has a :attr:`~Element.length_changed` signal, which gets emitted whenever the length of the element changes. You can check this yourself by connecting your own callback to the :attr:`~Element.length_changed` signal::

    >>> callback = lambda: print("This is a callback")
    >>> drift = ap.Drift('Drift', length=2)
    >>> drift.length_changed.connect(callback)
    >>> drift.length += 1
    This is a callback

This may not seem useful at first, but can be handy for different optimization tasks. Also apace internally heavily relies on this event system.

.. _lazy_eval:

Lazy Evaluation
---------------

In addition to the event system apace also makes use of `Lazy Evaluation <https://wikipedia.org/wiki/Lazy_evaluation>`_. This means that whenever an object changes its state, it  will only notify its dependents that an updated is needed. The recalculation of the dependents's new attribute will be delayed until the next time it is accessed.

This lazy evaluation scheme is especially important in combination with the signal system as it can prevent unnecessary calculations: Without the lazy evaluation scheme computational expensive properties will get recalculated whenever one of its dependents changes. With the lazy evaluation scheme they are only calculated if they are actually accessed.

To check if a property needs to be updated one can log the private variable :code:`_needs_update` variables::

   >>> drift = ap.Drift("Drift", length=2)
   >>> lattice = ap.Lattice('Lattice', drift)
   >>> drift.length = 1
   >>> lattice._length_needs_update
   True

.. warning::

    The :attr:`_needs_update` variables are meant for internal use only!

