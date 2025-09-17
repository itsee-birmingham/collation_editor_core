---
id: upgrade-1cor-dev
title: Changelog for 1cor-dev branch
sidebar_label: 1cor-dev branch
---

## html and css

+ The ids and class names which previously used underscores in the values have been changed to use dashes. If you are using 
ids or class names in your own css to change the look or behaviour of the collation editor these will need to be updated.
+ h1 tags in the header of the collation have been changed to spans, again this may affect any custom css.
+ A few of the classes/ids have changed to remove references specific to particular texts
    + the h1#verse_ref is now span#unit-ref to remove the reference to verses.
    + the .NAword class is now .overtext-word.