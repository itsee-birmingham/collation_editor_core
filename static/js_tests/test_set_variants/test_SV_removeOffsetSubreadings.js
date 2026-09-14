/* global QUnit, sinon, CL, SV, SR*/

QUnit.module('SV _removeOffsetSubreadings', function (hooks) {

    const allRules = {
        "none": [undefined, false], "reconstructed": ["V", false], "unclear": ["V", false],
        "fehler": ["f", true], "fehlerSuff": ["f", false], "orthographic": ["o", true],
        "regularised": ["r", false], "abbreviation": ["a", false]
    };

    hooks.beforeEach(function () {

        CL.project = {};
        CL.project.prepareDisplayString = function (string) {
            return string;
        };
        CL.project.omCategories = [];

    });

    hooks.afterEach(function () {
        sinon.restore();
    });


    QUnit.test("test _removeOffsetSubreadings 1", (assert) => {
        /** test a case with no offset subreadings - data should not change */
        sinon.stub(CL, 'getRuleClasses').returns(allRules);

        CL.data = {
            "apparatus": [
                {
                    "readings": [
                        {
                            "witnesses": [
                                "basetext",
                                "01",
                                "33",
                                "P46",
                                "L60-S3W2D7",
                                "6"
                            ],
                            "text": [
                                {
                                    "6": {
                                        "_sigil": "6",
                                        "_token_array_position": 71,
                                        "decision_class": [
                                            "abbreviation"
                                        ],
                                        "decision_details": [
                                            {
                                                "class": "abbreviation",
                                                "id": 357594,
                                                "n": "θεου",
                                                "scope": "once",
                                                "t": "θυ"
                                            }
                                        ],
                                        "index": "12",
                                        "n": "θεου",
                                        "nomSac": true,
                                        "original": "θυ",
                                        "rule_match": [
                                            "θυ"
                                        ],
                                        "siglum": "6",
                                        "t": "θυ"
                                    },
                                    "33": {
                                        "_sigil": "33",
                                        "_token_array_position": 18,
                                        "decision_class": [
                                            "abbreviation"
                                        ],
                                        "decision_details": [
                                            {
                                                "class": "abbreviation",
                                                "id": 357591,
                                                "n": "θεου",
                                                "scope": "once",
                                                "t": "θυ"
                                            }
                                        ],
                                        "index": "12",
                                        "n": "θεου",
                                        "nomSac": true,
                                        "original": "θυ",
                                        "rule_match": [
                                            "θυ"
                                        ],
                                        "siglum": "33",
                                        "t": "θυ"
                                    },
                                    "reading": [
                                        "basetext",
                                        "01",
                                        "33",
                                        "P46",
                                        "L60-S3W2D7",
                                        "6"
                                    ],
                                    "verse": "Gal.1.3",
                                    "interface": "θεου",
                                    "basetext": {
                                        "_sigil": "basetext",
                                        "_token_array_position": 44,
                                        "index": "12",
                                        "lemma": "θεου",
                                        "original": "θεοῦ",
                                        "rule_match": [
                                            "θεου"
                                        ],
                                        "siglum": "basetext",
                                        "t": "θεου"
                                    },
                                    "index": "12.1",
                                    "01": {
                                        "_sigil": "01",
                                        "_token_array_position": 5,
                                        "decision_class": [
                                            "abbreviation"
                                        ],
                                        "decision_details": [
                                            {
                                                "class": "abbreviation",
                                                "id": 357590,
                                                "n": "θεου",
                                                "scope": "once",
                                                "t": "θυ"
                                            }
                                        ],
                                        "index": "12",
                                        "n": "θεου",
                                        "nomSac": true,
                                        "original": "θυ",
                                        "rule_match": [
                                            "θυ"
                                        ],
                                        "siglum": "01",
                                        "t": "θυ"
                                    },
                                    "P46": {
                                        "_sigil": "P46",
                                        "_token_array_position": 31,
                                        "decision_class": [
                                            "abbreviation"
                                        ],
                                        "decision_details": [
                                            {
                                                "class": "abbreviation",
                                                "id": 357592,
                                                "n": "θεου",
                                                "scope": "once",
                                                "t": "θυ"
                                            }
                                        ],
                                        "index": "12",
                                        "n": "θεου",
                                        "nomSac": true,
                                        "original": "θυ",
                                        "rule_match": [
                                            "θυ"
                                        ],
                                        "siglum": "P46",
                                        "t": "θυ"
                                    },
                                    "L60-S3W2D7": {
                                        "_sigil": "L60-S3W2D7",
                                        "_token_array_position": 58,
                                        "decision_class": [
                                            "abbreviation"
                                        ],
                                        "decision_details": [
                                            {
                                                "class": "abbreviation",
                                                "id": 357593,
                                                "n": "θεου",
                                                "scope": "once",
                                                "t": "θυ"
                                            }
                                        ],
                                        "index": "14",
                                        "n": "θεου",
                                        "nomSac": true,
                                        "original": "θυ",
                                        "rule_match": [
                                            "θυ"
                                        ],
                                        "siglum": "L60-S3W2D7",
                                        "t": "θυ"
                                    }
                                }
                            ],
                            "_id": "cb11e5b44551969c3fc62158cea88581"
                        }
                    ],
                    "start": 12,
                    "end": 12,
                    "first_word_index": "12.1",
                    "_id": "4fac220aa9fcffa6012c45820d761407"
                }
            ],
            "om_readings": [],
            "lac_readings": [],
            "special_categories": [],
            "hand_id_map": {
                "6": "NT_GRC_6_Gal",
                "33": "NT_GRC_33_Gal",
                "01": "NT_GRC_01_Gal",
                "P46": "NT_GRC_P46_Gal",
                "basetext": "NT_GRC_basetext_Gal",
                "L60-S3W2D7": "NT_GRC_L60_Gal"
            },
            "marked_readings": {},
            "separated_witnesses": []
        }

        const originalData = JSON.stringify(CL.data);
        // prepare the expected result
        CL.data = JSON.parse(originalData);
        SR.loseSubreadings();
        SR.findSubreadings();
        const expectedData = JSON.stringify(CL.data);
        // put the original back to run the test
        CL.data = JSON.parse(originalData);
        SV._removeOffsetSubreadings();
        assert.equal(expectedData, JSON.stringify(CL.data));
    });

    QUnit.test("test _removeOffsetSubreadings 2", (assert) => {
        /** test a case with no offset subreadings - data should not change */
        sinon.stub(CL, 'getRuleClasses').returns(allRules);

        CL.data = {
            "apparatus": [
                {
                    "readings": [
                        {
                            "witnesses": [
                                "01",
                                "33",
                                "basetext"
                            ],
                            "text": [
                                {
                                    "33": {
                                        "_sigil": "33",
                                        "_token_array_position": 20,
                                        "index": "16",
                                        "original": "ημων",
                                        "rule_match": [
                                            "ημων"
                                        ],
                                        "siglum": "33",
                                        "t": "ημων"
                                    },
                                    "reading": [
                                        "01",
                                        "33",
                                        "basetext"
                                    ],
                                    "verse": "Gal.1.3",
                                    "interface": "ημων",
                                    "01": {
                                        "_sigil": "01",
                                        "_token_array_position": 7,
                                        "index": "16",
                                        "original": "ημων",
                                        "rule_match": [
                                            "ημων"
                                        ],
                                        "siglum": "01",
                                        "t": "ημων"
                                    },
                                    "basetext": {
                                        "_sigil": "basetext",
                                        "_token_array_position": 46,
                                        "index": "16",
                                        "lemma": "ημων",
                                        "original": "ἡμῶν",
                                        "rule_match": [
                                            "ημων"
                                        ],
                                        "siglum": "basetext",
                                        "t": "ημων"
                                    },
                                    "index": "16.1"
                                }
                            ],
                            "_id": "1e3f145bc4c0a117b4af276ff5501cf4"
                        },
                        {
                            "_id": "1c4e939e8ffc52c632a389359de82b37",
                            "created": true,
                            "text": [
                                {
                                    "index": "0",
                                    "interface": "test",
                                    "reading": []
                                }
                            ],
                            "witnesses": [
                                "P46"
                            ],
                            "SR_text": {
                                "P46": {
                                    "text": [],
                                    "type": "om"
                                }
                            }
                        },
                        {
                            "witnesses": [
                                "L60-S3W2D7",
                                "6"
                            ],
                            "text": [],
                            "type": "om",
                            "_id": "6d35e2bd6d2c5f7d21f048bc40ffff19"
                        }
                    ],
                    "start": 16,
                    "end": 16,
                    "first_word_index": "16.1",
                    "_id": "53c957b31ea2139d2205ec42756e815c"
                }
            ],
            "om_readings": [],
            "lac_readings": [],
            "special_categories": [],
            "hand_id_map": {
                "6": "NT_GRC_6_Gal",
                "33": "NT_GRC_33_Gal",
                "01": "NT_GRC_01_Gal",
                "P46": "NT_GRC_P46_Gal",
                "basetext": "NT_GRC_basetext_Gal",
                "L60-S3W2D7": "NT_GRC_L60_Gal"
            },
            "marked_readings": {
                "reconstructed": [
                    {
                        "start": 16,
                        "end": 16,
                        "unit_id": "53c957b31ea2139d2205ec42756e815c",
                        "first_word_index": "16.1",
                        "witness": "P46",
                        "apparatus": "apparatus",
                        "reading_text": "om.",
                        "parent_text": "test",
                        "identifier": [
                            "V"
                        ],
                        "suffixed_sigla": [
                            true
                        ],
                        "suffixed_label": [
                            false
                        ],
                        "reading_history": [
                            "om."
                        ],
                        "value": "reconstructed",
                        "subreading": [
                            false
                        ],
                        "name": [
                            "Reconstructed"
                        ],
                        "type": "om"
                    }
                ]
            },
            "separated_witnesses": []
        };
        const originalData = JSON.stringify(CL.data);
        let expectedData = JSON.parse(originalData);
        const expectedChangedReading = {
            "witnesses": [
                "P46"
            ],
            "text": [],
            "type": "om",
            "_id": ""
        }
        expectedData.apparatus[0].readings[1] = expectedChangedReading;
        expectedData = JSON.stringify(expectedData);

        // put the original back to run the test
        CL.data = JSON.parse(originalData);
        SV._removeOffsetSubreadings();
        SR.loseSubreadings();
        // remove the _id value because it will be unpredictable
        CL.data.apparatus[0].readings[1]._id = "";
        assert.equal(expectedData, JSON.stringify(CL.data));

        // now check if we can find the subreadings again and lose them (always have to lose them first)
        // and end up back where we started
        SR.loseSubreadings();
        SR.findSubreadings();
        SR.loseSubreadings();
        let newExpectedData = JSON.parse(originalData);
        newExpectedData.apparatus[0].readings[1]._id = "";
        newExpectedData = JSON.stringify(newExpectedData);
        CL.data.apparatus[0].readings[1]._id = "";
        assert.equal(newExpectedData, JSON.stringify(CL.data));
    });

});