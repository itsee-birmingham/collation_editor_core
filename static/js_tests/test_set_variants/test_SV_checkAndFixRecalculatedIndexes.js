/* global QUnit, sinon, SV */

QUnit.module('SV _checkAndFixRecalculatedIndexes', function(hooks) {

    hooks.afterEach(function () {
        sinon.restore();
    });

    QUnit.test("test a no indexing missing", (assert) => {

        const reading = {
            'text': [
                {'index': '2.1'},
                {'index': '4.1'},
                {'index': '6.1'},
                {'index': '8.1'},
                {'index': '10.1'},
            ],
        } 
        SV._checkAndFixRecalculatedIndexes(reading, 2, 10);
        assert.deepEqual(reading.text.map(x => x.index), ['2.1', '4.1', '6.1', '8.1', '10.1'])
    });

    QUnit.test("test a simple reindex with no length difference", (assert) => {

        const reading = {
            'text': [
                {'index': '2.1'},
                {'index': '2.2'},
                {'index': '2.3'},
                {'index': '2.4'},
                {'index': '10.1'},
            ],
        } 
        SV._checkAndFixRecalculatedIndexes(reading, 2, 10);
        assert.deepEqual(reading.text.map(x => x.index), ['2.1', '4.1', '6.1', '8.1', '10.1'])
    });

    QUnit.test("test a simple reindex with shorter reading", (assert) => {

        const reading = {
            'text': [
                {'index': '2.1'},
                {'index': '2.2'},
                {'index': '2.3'},
                {'index': '10.1'},
            ],
        } 
        SV._checkAndFixRecalculatedIndexes(reading, 2, 10);
        assert.deepEqual(reading.text.map(x => x.index), ['2.1', '4.1', '6.1', '10.1'])
    });

    QUnit.test("test a simple reindex with longer reading", (assert) => {

        const reading = {
            'text': [
                {'index': '2.1'},
                {'index': '2.2'},
                {'index': '2.3'},
                {'index': '2.4'},
                {'index': '2.5'},
                {'index': '2.6'},
                {'index': '10.1'},
            ],
        } 
        SV._checkAndFixRecalculatedIndexes(reading, 2, 10);
        assert.deepEqual(reading.text.map(x => x.index), ['2.1', '4.1', '6.1', '8.1', '8.2', '8.3','10.1'])
    });

    QUnit.test("test a simple reindex with longer reading more at end too", (assert) => {

        const reading = {
            'text': [
                {'index': '2.1'},
                {'index': '2.2'},
                {'index': '2.3'},
                {'index': '2.4'},
                {'index': '2.5'},
                {'index': '2.6'},
                {'index': '10.1'},
                {'index': '10.2'},
                {'index': '10.3'},
            ],
        } 
        SV._checkAndFixRecalculatedIndexes(reading, 2, 10);
        assert.deepEqual(reading.text.map(x => x.index), ['2.1', '4.1', '6.1', '8.1', '8.2', '8.3','10.1', '10.2', '10.3'])
    });

    QUnit.test("test a reindex with a first position change", (assert) => {

        const reading = {
            'text': [
                {'index': '1.1000'},
                {'index': '4.1'},
                {'index': '4.2'},
                {'index': '10.1'},
            ],
        }
        SV._checkAndFixRecalculatedIndexes(reading, 2, 10);
        assert.deepEqual(reading.text.map(x => x.index), ['2.1', '4.1', '6.1', '10.1'])
    });

    QUnit.test("test a reindex with a first position change", (assert) => {

        const reading = {
            'text': [
                {'index': '1.1000'},
                {'index': '2.1'},
                {'index': '4.1'},
                {'index': '10.1'},
            ],
        }
        SV._checkAndFixRecalculatedIndexes(reading, 2, 10);
        assert.deepEqual(reading.text.map(x => x.index), ['1.1000', '2.1', '4.1', '10.1'])
    });

    QUnit.test("test a reindex with odd number", (assert) => {

        const reading = {
            'text': [
                {'index': '2.1'},
                {'index': '3.1'},
                {'index': '4.1'},
                {'index': '4.2'},
                {'index': '10.1'},
            ],
        }
        SV._checkAndFixRecalculatedIndexes(reading, 2, 10);
        assert.deepEqual(reading.text.map(x => x.index), ['2.1', '3.1', '4.1', '6.1', '10.1'])
    });

    QUnit.test("test a reindex with odd number at end", (assert) => {

        const reading = {
            'text': [
                {'index': '2.1'},
                {'index': '3.1'},
                {'index': '4.1'},
                {'index': '4.2'},
                {'index': '9.1'},
            ],
        }
        SV._checkAndFixRecalculatedIndexes(reading, 2, 10);
        assert.deepEqual(reading.text.map(x => x.index), ['2.1', '3.1', '4.1', '6.1', '9.1'])
    });

    QUnit.test("test a reindex with odd number after repeat (should not change)", (assert) => {

        const reading = {
            'text': [
                {'index': '2.1'},
                {'index': '2.2'},
                {'index': '3.1'},
                {'index': '4.1'},
                {'index': '10.1'},
            ],
        }
        SV._checkAndFixRecalculatedIndexes(reading, 2, 10);
        assert.deepEqual(reading.text.map(x => x.index), ['2.1', '2.2', '3.1', '4.1', '10.1'])
    });

    QUnit.test("test a reindex with odd number after multiple repeats (should not change)", (assert) => {

        const reading = {
            'text': [
                {'index': '2.1'},
                {'index': '2.2'},
                {'index': '2.3'},
                {'index': '3.1'},
                {'index': '10.1'},
            ],
        }
        SV._checkAndFixRecalculatedIndexes(reading, 2, 10);
        assert.deepEqual(reading.text.map(x => x.index), ['2.1', '2.2', '2.3', '3.1', '10.1'])
    });

    QUnit.test("test a reindex with odd number after multiple repeats which also needs changes", (assert) => {

        const reading = {
            'text': [
                {'index': '2.1'},
                {'index': '2.2'},
                {'index': '2.3'},
                {'index': '3.1'},
                {'index': '4.1'},
                {'index': '4.2'},
                {'index': '4.3'},
                {'index': '4.4'},
                {'index': '10.1'},
            ],
        }
        SV._checkAndFixRecalculatedIndexes(reading, 2, 10);
        assert.deepEqual(reading.text.map(x => x.index), ['2.1', '2.2', '2.3', '3.1', '4.1', '6.1', '8.1','8.2', '10.1'])
    });

});