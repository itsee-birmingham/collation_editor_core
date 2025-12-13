/* global QUnit, sinon, CL, SV */

QUnit.module('SV _reindexMovedReadingByMatching', function(hooks) {

    hooks.afterEach(function () {
        sinon.restore();
    });

    QUnit.test("test no words have exact matches", (assert) => {
        const readings = [
            {'witnesses': ['01'], 'text': [
                {'interface': 'one', 'index': '2.1'},
                {'interface': 'two', 'index': '4.1'},
            ]},
            {'witnesses': ['P45'], 'text': [
                {'interface': 'once'},
                {'interface': 'twice'},
            ]}
        ];
        CL.data = {
            'apparatus': [
                {
                    'start': 2,
                    'end': 4,
                    'readings': readings}
            ]
        };
        SV._reindexMovedReadingByMatching(2, 'P45');
        // TODO: this ideally should be ['2.1', '4.1']
        assert.deepEqual(readings[1].text.map(x => x.index), ['2.1', '4.1'])
    });

    QUnit.test("test no readings have indexes yet (should probably never happen)", (assert) => {
        const readings = [
            {'witnesses': ['01'], 'text': [
                {'interface': 'one'},
                {'interface': 'two'},
            ]},
            {'witnesses': ['P45'], 'text': [
                {'interface': 'once'},
                {'interface': 'twice'},
            ]}
        ];
        CL.data = {
            'apparatus': [
                {
                    'start': 2,
                    'end': 4,
                    'readings': readings}
            ]
        };
        SV._reindexMovedReadingByMatching(2, 'P45');
        // TODO: this ideally should be ['2.1', '4.1']
        assert.deepEqual(readings[1].text.map(x => x.index), ['2.1', '4.1'])
    });

    QUnit.test("test first word has exact match", (assert) => {
        const readings = [
            {'witnesses': ['01'], 'text': [
                {'interface': 'one', 'index': '2.1'},
                {'interface': 'two', 'index': '4.1'},
            ]},
            {'witnesses': ['P45'], 'text': [
                {'interface': 'one'},
                {'interface': 'twice'},
            ]}
        ];
        CL.data = {
            'apparatus': [
                {
                    'start': 2,
                    'end': 4,
                    'readings': readings}
            ]
        };

        SV._reindexMovedReadingByMatching(2, 'P45');
        // TODO: this ideally should be ['2.1', '4.1']
        assert.deepEqual(readings[1].text.map(x => x.index), ['2.1', '4.1'])
    });

    QUnit.test("test second word has exact match", (assert) => {
        const readings = [
            {'witnesses': ['01'], 'text': [
                {'interface': 'one', 'index': '2.1'},
                {'interface': 'two', 'index': '4.1'},
            ]},
            {'witnesses': ['P45'], 'text': [
                {'interface': 'once'},
                {'interface': 'two'},
            ]}
        ];
        CL.data = {
            'apparatus': [
                {
                    'start': 2,
                    'end': 4,
                    'readings': readings}
            ]
        };

        SV._reindexMovedReadingByMatching(2, 'P45');
        assert.deepEqual(readings[1].text.map(x => x.index), ['2.1', '4.1'])
    });

    QUnit.test("test different lengths no first word match", (assert) => {
        const readings = [
            {'witnesses': ['01'], 'text': [
                {'interface': 'one', 'index': '2.1'},
                {'interface': 'two', 'index': '4.1'},
            ]},
            {'witnesses': ['P45'], 'text': [
                {'interface': 'zero'},
                {'interface': 'one'},
                {'interface': 'two'},
            ]}
        ];
        CL.data = {
            'apparatus': [
                {
                    'start': 2,
                    'end': 4,
                    'readings': readings}
            ]
        };
        SV._reindexMovedReadingByMatching(2, 'P45');
        assert.deepEqual(readings[1].text.map(x => x.index), ['1.1000', '2.1', '4.1'])
    });

    QUnit.test("test different lengths no middle word match", (assert) => {
        const readings = [
            {'witnesses': ['01'], 'text': [
                {'interface': 'one', 'index': '2.1'},
                {'interface': 'two', 'index': '4.1'},
            ]},
            {'witnesses': ['P45'], 'text': [
                {'interface': 'one'},
                {'interface': 'middle'},
                {'interface': 'two'},
            ]}
        ];
        CL.data = {
            'apparatus': [
                {
                    'start': 2,
                    'end': 4,
                    'readings': readings}
            ]
        };
        SV._reindexMovedReadingByMatching(2, 'P45');
        assert.deepEqual(readings[1].text.map(x => x.index), ['2.1', '2.2', '4.1'])
    });

    QUnit.test("test different lengths no end word match", (assert) => {
        const readings = [
            {'witnesses': ['01'], 'text': [
                {'interface': 'one', 'index': '2.1'},
                {'interface': 'two', 'index': '4.1'},
            ]},
            {'witnesses': ['P45'], 'text': [
                {'interface': 'one'},
                {'interface': 'two'},
                {'interface': 'three'},
            ]}
        ];
        CL.data = {
            'apparatus': [
                {
                    'start': 2,
                    'end': 4,
                    'readings': readings}
            ]
        };
        SV._reindexMovedReadingByMatching(2, 'P45');
        assert.deepEqual(readings[1].text.map(x => x.index), ['2.1', '4.1', '4.2'])
    });

    QUnit.test("test different lengths offset matches", (assert) => {
        const readings = [
            {'witnesses': ['01'], 'text': [
                {'interface': 'one', 'index': '2.1'},
                {'interface': 'two', 'index': '4.1'},
                {'interface': 'three', 'index': '6.1'},
            ]},
            {'witnesses': ['P45'], 'text': [
                {'interface': 'one'},
                {'interface': 'half'},
                {'interface': 'two'},
            ]}
        ];
        CL.data = {
            'apparatus': [
                {
                    'start': 2,
                    'end': 6,
                    'readings': readings}
            ]
        };
        SV._reindexMovedReadingByMatching(2, 'P45');
        assert.deepEqual(readings[1].text.map(x => x.index), ['2.1', '2.2', '4.1'])
    });

    QUnit.test("test different lengths repeated word in moved", (assert) => {
        const readings = [
            {'witnesses': ['01'], 'text': [
                {'interface': 'one', 'index': '2.1'},
                {'interface': 'two', 'index': '4.1'},
                {'interface': 'three', 'index': '6.1'},
            ]},
            {'witnesses': ['P45'], 'text': [
                {'interface': 'one'},
                {'interface': 'one'},
                {'interface': 'three'},
            ]}
        ];
        CL.data = {
            'apparatus': [
                {
                    'start': 2,
                    'end': 6,
                    'readings': readings}
            ]
        };
        SV._reindexMovedReadingByMatching(2, 'P45');
        // TODO: would ideally be 2.1, 4.1, 6.1
        assert.deepEqual(readings[1].text.map(x => x.index), ['2.1', '4.1', '6.1'])
    });

    QUnit.test("test different lengths repeated word in closest match", (assert) => {
        const readings = [
            {'witnesses': ['01'], 'text': [
                {'interface': 'one', 'index': '2.1'},
                {'interface': 'one', 'index': '4.1'},
                {'interface': 'three', 'index': '6.1'},
            ]},
            {'witnesses': ['P45'], 'text': [
                {'interface': 'one'},
                {'interface': 'two'},
                {'interface': 'three'},
            ]}
        ];
        CL.data = {
            'apparatus': [
                {
                    'start': 2,
                    'end': 6,
                    'readings': readings}
            ]
        };
        SV._reindexMovedReadingByMatching(2, 'P45');
        // TODO: would ideally be 2.1, 4.1, 6.1
        assert.deepEqual(readings[1].text.map(x => x.index), ['2.1', '4.1', '6.1'])
    });

});