/* global QUnit, sinon, CL, SV */

QUnit.module('SV _combineUnits', function(hooks) {

    const allRules = {"none": [undefined, false], "reconstructed": ["V", false], "unclear": ["V", false],
                      "fehler": ["f", true], "fehlerSuff": ["f", false], "orthographic": ["o", true],
                      "regularised": ["r", false], "abbreviation": ["a", false], "nomsac": ["n", false]};

    hooks.beforeEach(function () {

        CL.project = {};
        CL.project.prepareDisplayString = function (string) {
            return string;
        };

    });

    hooks.afterEach(function () {
        sinon.restore();
    });

    QUnit.test("test _combineUnits 1", (assert) => {
        /** test two units combining at the same index point where one word in the second is regularised to lac and 
         * will be combining with an om */
        sinon.stub(CL, 'getRuleClasses').returns(allRules);
        sinon.stub(CL, 'getCollationHeader').returns([['<div>header row</div>'], 2]);

        const unit1Readings = [
            {
                "type": "om", "text": [], "witnesses": ["1", "2"]
            },
            {
                "text": [{"3": {}, "interface": "one", "index": "3.1", "reading": ["3"]}], "witnesses": ["3"]
            }
        ];
        const unit2Readings = [
            {
                "type": "om", "text": [], "witnesses": ["1"]
            },
            {
                "text": [{"3": {}, "interface": "two", "index": "3.2", "reading": ["3"]}], "witnesses": ["3"]
            },
            {
                "type": "lac", "details": "lac", "created": true, "text": [], "witnesses": ["2"],
                "SR_text": {
                    "2": {"text": [{"2": {}, "interface": "[two]", "index": "3.2", "reading": ["2"]}]},
                }
            }
        ];
        const unit3Readings = [
            {
                "text": [{"1": {}, "2": {}, "3": {}, "interface": "three", "index": "4.1", "reading": ["1", "2", "3"]}], "witnesses": ["1", "2", "3"]
            }
        ];
        const apparatus = [
            {
                "start": 3, "end": 3, "first_word_index": "3.1", "_id": "abc123", "readings": unit1Readings
            },
            {
                "start": 3, "end": 3, "first_word_index": "3.2", "_id": "def123", "readings": unit2Readings
            },
            {
                "start": 4, "end": 4, "first_word_index": "4.1", "_id": "ghi123", "readings": unit3Readings
            }
        ];
        const markedReadings = {"none":
            [
                {
                    "start": 3,
                    "end": 3,
                    "unit_id": "def123",
                    "first_word_index": "3.2",
                    "apparatus": "apparatus",
                    "name": ["None"],
                    "om_details": "lac",
                    "parent_text": "&lt;lac&gt;",
                    "value": "none",
                    "witness": "2",
                    "reading_text": "[two]",
                }
            ]
        };
        CL.data = {"apparatus": apparatus, "marked_readings": markedReadings, "lac_readings": [], "om_readings": []};
        SV._combineUnits([[0, "apparatus", undefined], [1, "apparatus", undefined]]);
        console.log(CL.data)

        assert.equal(CL.data.apparatus.length, 1);

    });

});