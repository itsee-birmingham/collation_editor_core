var drag = (function () {
    "use strict";

    // private variables
    let _behaviours = {};
    let _startX, _startY, _dragElement;

    // private functions
    let _dragMouseDown, _elementDrag, _closeDragElement;
    //public functions
    let initDraggable;

    initDraggable = function (elemId, x, y) {
      let element, dragZone;
      if (!document.getElementById(elemId)) {
        return false;
      }
      element = document.getElementById(elemId);
      _dragElement = element
      dragZone = element.querySelectorAll('.drag-zone');
      if (dragZone.length === 1) {
        // if there is a drag-zone specified only drag by that
        dragZone[0].onmousedown = _dragMouseDown;
      } else {
        // else drag from anywhere
        element.onmousedown = _dragMouseDown;
      }
      // set permitted behaviour booleans
      _behaviours[elemId] = {};
      if (typeof x !== 'undefined') {
        _behaviours[elemId]['horizontal'] = x;
      }
      if (typeof y !== 'undefined') {
        _behaviours[elemId]['vertical'] = y;
      }
    };

    _dragMouseDown = function (e) {
      e = e || window.event;
      e.preventDefault();
      // get the mouse cursor position at startup:
      _startX = _dragElement.clientX;
      _startY = _dragElement.clientY;
      document.onmouseup = _closeDragElement;
      // call a function whenever the cursor moves:
      document.onmousemove = _elementDrag;
    };

    _elementDrag = function (e) {
      let endX, endY;
      e = e || window.event;
      e.preventDefault();
      // calculate the new cursor position for the enabled axis
      if (_behaviours[_dragElement.id]['horizontal'] === true) {
        endX = _startX - e.clientX;
        _startX = e.clientX;
      } else {
        endX = _startX;
      }
      if (_behaviours[_dragElement.id]['vertical'] === true) {
        endY = _startY - e.clientY;
        _startY = e.clientY;
      } else {
        endY = _startY;
      }
      // set the element's new position:
      _dragElement.style.top = (_dragElement.offsetTop - endY) + "px";
      _dragElement.style.left = (_dragElement.offsetLeft - endX) + "px";
    };

    _closeDragElement = function () {
      // stop moving when mouse button is released:
      document.onmouseup = null;
      document.onmousemove = null;
    };

    return {
            initDraggable: initDraggable
            };

}());
