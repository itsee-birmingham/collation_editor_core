/* global QUnit, sinon, SV */

QUnit.module('SV _getSharedWordsList', function(hooks) {

    hooks.afterEach(function () {
        sinon.restore();
    });

    QUnit.test("test shared words in order no duplicates", (assert) => {
        const closestReadingWords = ['one', 'two', 'three', 'four'];
        const movedReadingWords = ['one', 'two', 'three', 'four'];
        const result = SV._getSharedWordsList(closestReadingWords, movedReadingWords);
        assert.deepEqual(result, ['one', 'two', 'three', 'four']);
    });

    QUnit.test("test shared words out of order no duplicates", (assert) => {
        const closestReadingWords = ['one', 'two', 'three', 'four'];
        const movedReadingWords = ['two', 'three', 'one', 'four'];
        const result = SV._getSharedWordsList(closestReadingWords, movedReadingWords);
        assert.deepEqual(result, ['two', 'three', 'four']);
    });

    QUnit.test("test shared words more out of order no duplicates 1", (assert) => {
        const closestReadingWords = ['one', 'two', 'three', 'four'];
        const movedReadingWords = ['two', 'one', 'four', 'three'];
        const result = SV._getSharedWordsList(closestReadingWords, movedReadingWords);
        assert.deepEqual(result, ['two', 'four']);
    });

    QUnit.test("test shared words more out of order with duplicates 2", (assert) => {
        const closestReadingWords = ['one', 'two', 'two', 'three', 'four'];
        const movedReadingWords = ['one', 'two', 'four', 'one', 'four', 'three'];
        const result = SV._getSharedWordsList(closestReadingWords, movedReadingWords);
        assert.deepEqual(result, ['one', 'two', 'four']);
    });

    QUnit.test("test shared words more out of order with duplicates 3", (assert) => {
        const closestReadingWords = ['one', 'four', 'two', 'two', 'three', 'four'];
        const movedReadingWords = ['one', 'two', 'four', 'one', 'four', 'three'];
        const result = SV._getSharedWordsList(closestReadingWords, movedReadingWords);
        assert.deepEqual(result, ['one', 'two', 'four']);
    });

    QUnit.test("test shared words more out of order with duplicates 3", (assert) => {
        const closestReadingWords = ['one', 'four', 'two', 'two', 'three'];
        const movedReadingWords = ['one', 'two', 'four', 'one', 'four', 'three'];
        const result = SV._getSharedWordsList(closestReadingWords, movedReadingWords);
        assert.deepEqual(result, ['one', 'two', 'three']);
    });


});