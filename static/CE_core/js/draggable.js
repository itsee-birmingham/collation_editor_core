var drag = (function () {
    "use strict";

    // private variables
    let _behaviours = {};
    let _startX, _startY, _startZIndex;

    // private functions
    let _dragMouseDown, _mouseDrag, _closeDragElement, _dragElement;
    //public functions
    let initDraggable;

    initDraggable = function (elemId, x, y) {
      let element, dragZone;
      if (!document.getElementById(elemId)) {
        return false;
      }
      element = document.getElementById(elemId);
      dragZone = element.querySelectorAll('.drag-zone');
      if (dragZone.length === 1) {
        // if there is a drag-zone specified only drag by that
        dragZone[0].onmousedown = _dragMouseDown;
        dragZone[0].setAttribute('data-drags', elemId);
      } else {
        // else drag from anywhere
        element.onmousedown = _dragMouseDown;
        element.setAttribute('data-drags', elemId);
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
      console.log(e.target);
      e.preventDefault();
      _dragElement = document.getElementById(e.target.getAttribute('data-drags'));
      // get the mouse cursor position at startup:
      _startX = _dragElement.clientX;
      _startY = _dragElement.clientY;
      _startZIndex = _dragElement.style.zIndex;
      _dragElement.style.zIndex = 40000;
      document.onmouseup = _closeDragElement;
      // call a function whenever the cursor moves:
      document.onmousemove = _mouseDrag;
    };

    _mouseDrag = function (e) {
      let newLeft, newRight, newTop, newBase;
      e = e || window.event;
      e.preventDefault();
      // calculate the new cursor position for the enabled axis
      if (_behaviours[_dragElement.id]['horizontal'] === true) {
        newLeft = _dragElement.offsetLeft +  e.clientX - _startX;
        newRight = newLeft + _dragElement.offsetWidth;
        _startX = e.clientX;
        if (newLeft > 0 && newRight < window.innerWidth) {
          _dragElement.style.left = newLeft + "px";
        }
      }
      if (_behaviours[_dragElement.id]['vertical'] === true) {
        newTop = _dragElement.offsetTop + e.clientY - _startY;
        newBase = newTop + _dragElement.offsetHeight;
        _startY = e.clientY;
        if (newTop > 0 && newBase < window.innerHeight) {
          _dragElement.style.top = newTop + "px";
        }
      }
    };

    _closeDragElement = function () {
      // stop moving when mouse button is released:
      _dragElement.style.zIndex = _startZIndex;
      _dragElement = null;
      document.onmouseup = null;
      document.onmousemove = null;
    };

    return {
            initDraggable: initDraggable
            };

}());
