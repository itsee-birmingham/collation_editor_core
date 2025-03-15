/* exported SR */
/* global CL, SV */
var SR = (function () {

  const _test = false;  // this is a flag which produces a very verbose console output for debugging. It should never be
                        // set to true in production because the volume of output makes it very slow.

  return {

    /**This identifies readings that could have subreadings and separates them from their parent reading in the
     * datastructure. It looks at the decisions added in RG and any standoff markup added in SV
     * the first type get sent of to SR._make_subreading and from there _addToSubreadings
     * the latter type get sent straight to _addToSubreadings
     * This function directly manipulates the data structure CL._JSON.input there is no return value
     *
     * @method findSubreadings
     * @param {dict} options (optional)
     *        rule_classes: A dictionary of rule classes that are to be extracted
     * 					(generated by CL.getRuleClasses function)
     * 					if not supplied then subreadings of all rule classes will be extracted
     * */
    findSubreadings: function (findOptions) {
      let parent, child, childPos, apparatus, readings, subreadings, forDeletion, options,
        markedReading, ruleClasses, unit, unitPos, readingPos;
      if (_test) {
        console.log('SR.findSubreadings');
      }
      if (typeof findOptions === 'undefined') {
        findOptions = {};
      }
      if (Object.prototype.hasOwnProperty.call(findOptions, 'rule_classes')) {
        ruleClasses = findOptions.rule_classes;
      }
      for (const key in CL.data) {
        if (Object.prototype.hasOwnProperty.call(CL.data, key)) {
          if (key.indexOf('apparatus') !== -1) {
            apparatus = CL.data[key];
            for (let i = 0; i < apparatus.length; i += 1) {
              readings = apparatus[i].readings;
              forDeletion = [];
              // this deals with the words regularised in RG
              for (let j = 0; j < readings.length; j += 1) {
                readings[j] = SR._makeSubreadings(readings[j], ruleClasses);
              }
              // this deals with the stand off marked readings (i.e. those created in set variants)
              for (const type in CL.data.marked_readings) {
                if (Object.prototype.hasOwnProperty.call(CL.data.marked_readings, type)) {
                  for (let j = 0; j < CL.data.marked_readings[type].length; j += 1) {
                    markedReading = CL.data.marked_readings[type][j];
                    if (markedReading.apparatus === key) { //if in right apparatus row
                      if (markedReading.start === apparatus[i].start &&
                        markedReading.end === apparatus[i].end) { //if unit extent is correct
                        // find the child reading
                        [child, childPos] = SR._findChildReading(apparatus[i], markedReading, _test);
                        if (_test) {
                          console.log('child is...');
                          console.log(child);
                        }
                        // get the parent
                        parent = SR._findParentReading(apparatus[i], key, markedReading, true, childPos);
                        if (_test) {
                          console.log('parent is...');
                          console.log(parent);
                        }
                        if (parent !== null) {
                          if (Object.prototype.hasOwnProperty.call(parent, 'subreadings')) {
                            subreadings = parent.subreadings;
                          } else {
                            subreadings = {};
                          }
                          if (child !== null) {
                            markedReading.applied = true;
                            SR._addCombinedGapDataToParent(parent, markedReading);
                            // sort out the options
                            options = {
                              'standoff': true
                            };
                            if (typeof ruleClasses !== 'undefined') {
                              options.rules = ruleClasses;
                            }
                            if (typeof markedReading.reading_text !== 'undefined') {
                              options.text = markedReading.reading_text;
                              options.text = SR._getCorrectStandoffReadingText(markedReading, ruleClasses);
                            }
                            if (typeof markedReading.combined_gap_before !== 'undefined') {
                              options.combined_gap_before = markedReading.combined_gap_before;
                            }
                            if (typeof markedReading.combined_gap_after !== 'undefined') {
                              options.combined_gap_after = markedReading.combined_gap_after;
                            }
                            if (typeof markedReading.combined_gap_before_details !== 'undefined') {
                              options.combined_gap_before_details = markedReading.combined_gap_before_details;
                            }
                            if (Object.prototype.hasOwnProperty.call(child, 'parents')) {
                              parent.parents = child.parents;
                            }
                            if (_test) {
                              console.log(options);
                              console.log(JSON.parse(JSON.stringify(subreadings)));
                            }
                            // then make the subreading for that witness (you might have to split a reading)
                            subreadings = SR._addToSubreadings(subreadings, child, markedReading.witness,
                                                               markedReading.value.split('|'), options);
                            if (SR._witnessIn(subreadings, markedReading.witness)) {
                              parent.subreadings = subreadings;
                              forDeletion.push([markedReading.witness, child]);
                            }
                            // for each reading we need to record the witnesses that were made subreading by standoff
                            // readings rather than regularised readings. This is so we can put all standoff
                            // subreadings in SR_text when we lose them (makes extracting text easier)
                            if (!Object.prototype.hasOwnProperty.call(parent, 'standoff_subreadings')) {
                              parent.standoff_subreadings = [];
                            }
                            if (parent.standoff_subreadings.indexOf(markedReading.witness) === -1) {
                              parent.standoff_subreadings.push(markedReading.witness);
                            }
                          }
                        }
                      }
                    }
                  }
                }
              }
              SR._removeFromMainReading(forDeletion);
              for (let j = 0; j < apparatus[i].readings.length; j += 1) {
                if (apparatus[i].readings[j].witnesses.length === 0 &&
                  !Object.prototype.hasOwnProperty.call(apparatus[i].readings[j], 'subreadings')) {
                  apparatus[i].readings[j] = null;
                }
              }
              CL.removeNullItems(apparatus[i].readings);
            }
          }
        }
      }
      SR._cleanStandoffMarking();  // clean the lot
      if (Object.prototype.hasOwnProperty.call(CL.data, 'separated_witnesses')) {
        for (let i = 0; i < CL.data.separated_witnesses.length; i += 1) {
          unit = CL.findUnitById(CL.data.separated_witnesses[i].app_id, CL.data.separated_witnesses[i].unit_id);
          unitPos = CL.findUnitPosById(CL.data.separated_witnesses[i].app_id, CL.data.separated_witnesses[i].unit_id);
          for (let j = 0; j < unit.readings.length; j += 1) {
            if (unit.readings[j].witnesses.indexOf(CL.data.separated_witnesses[i].witnesses[0]) !== -1) {
              readingPos = j;
            } else if (Object.prototype.hasOwnProperty.call(unit.readings[j], 'subreadings')) {
              for (const key in unit.readings[j].subreadings) {
                for (let k = 0; k < unit.readings[j].subreadings[key].length; k += 1) {
                  if (unit.readings[j].subreadings[key][k].witnesses.indexOf(CL.data.separated_witnesses[i].witnesses[0]) !== -1) {
                    readingPos = j;
                  }
                }
              }
            }
          }
          SV.doSplitReadingWitnesses(unitPos, readingPos, CL.data.separated_witnesses[i].witnesses,
            CL.data.separated_witnesses[i].app_id, false,
            CL.data.separated_witnesses[i].reading_id);
        }
      }
    },

    /** This merges the subreadings back in with their parent readings */
    loseSubreadings: function () {
      let apparatus, readings, reading;
      const data = CL.data;
      for (const key in data) {
        if (Object.prototype.hasOwnProperty.call(data, key)) {
          if (key.indexOf('apparatus') !== -1) {  // loop through lines of apparatus
            apparatus = data[key];
            for (let i = 0; i < apparatus.length; i += 1) {  // loop through units in apparatus
              readings = apparatus[i].readings;
              for (let j = 0; j < readings.length; j += 1) {  // loop through readings in unit
                reading = readings[j];
                if (Object.prototype.hasOwnProperty.call(reading, 'subreadings')) {  // if there are subreadings
                  SR._doLoseSubreadings(reading);
                }
              }
            }
          }
        }
      }
      // console.log('RESULT OF LOSE SUBREADINGS BELOW')
      // console.log(JSON.parse(JSON.stringify(CL.data)))
    },

    updateMarkedReadingData: function (unit, options) {
      let witnesses, standoffReading;
      witnesses = [];
      for (let i = 0; i < unit.readings.length; i += 1) {
        if (Object.prototype.hasOwnProperty.call(unit.readings[i], 'standoff_subreadings')) {
          witnesses = witnesses.concat(unit.readings[i].standoff_subreadings);
        }
        if (Object.prototype.hasOwnProperty.call(unit.readings[i], 'SR_text')) {
          witnesses = witnesses.concat(unit.readings[i].witnesses);
        }
      }
      for (let i = 0; i < witnesses.length; i += 1) {
        standoffReading = SR.getMatchingStandoffReading(witnesses[i], unit);
        if (standoffReading !== null) {
          if (Object.prototype.hasOwnProperty.call(options, 'end')) {
            standoffReading.end = options.end;
          }
          if (Object.prototype.hasOwnProperty.call(options, 'row')) {
            standoffReading.apparatus = 'apparatus' + options.row;
          }
        }
      }
    },

    getMatchingStandoffReading: function (witness, unit) {
      if (Object.prototype.hasOwnProperty.call(CL.data, 'marked_readings')) {
        for (const type in CL.data.marked_readings) {
          if (Object.prototype.hasOwnProperty.call(CL.data.marked_readings, type)) {
            for (let i = 0; i < CL.data.marked_readings[type].length; i += 1) {
              if (CL.data.marked_readings[type][i].apparatus === 'apparatus' + unit.row) {
                if (CL.data.marked_readings[type][i].start === unit.start &&
                  CL.data.marked_readings[type][i].end === unit.end) {
                  if (CL.data.marked_readings[type][i].witness === witness) {
                    return CL.data.marked_readings[type][i];
                  }
                }
              }
            }
          }
        }
      }
      return null;
    },

    _getCorrectStandoffReadingText: function (markedReading, ruleClasses) {
      let foundReading;
      if (typeof ruleClasses === 'undefined') {
        return markedReading.reading_text;
      }
      const ruleList = [];
      for (const key in ruleClasses) {
        if (Object.prototype.hasOwnProperty.call(ruleClasses, key)) {
          ruleList.push(key);
        }
      }
      const values = markedReading.value.split('|');
      for (let i = values.length - 1; i >= 0; i -= 1) {
        if (ruleList.indexOf(values[i]) !== -1 && Object.prototype.hasOwnProperty.call(markedReading, 'reading_history')) {
          foundReading = markedReading.reading_history[i];
        }
      }
      if (typeof foundReading !== 'undefined') {
        return foundReading;
      } else {
        return markedReading.reading_text;
      }
    },

    _addCombinedGapDataToParent: function (parent, standoffData) {
      // put subreadings combined gap data in now
      if (Object.prototype.hasOwnProperty.call(standoffData, 'combined_gap_after')) {
        if (parent.text.length > 0) {
          parent.text[parent.text.length - 1].combined_gap_after = [];
        }
        if (Object.prototype.hasOwnProperty.call(parent, 'combined_gap_after_subreadings')) {
          if (parent.combined_gap_after_subreadings.indexOf(standoffData.witness) === -1) {
            parent.combined_gap_after_subreadings.push(standoffData.witness);
          }
        } else {
          parent.combined_gap_after_subreadings = [standoffData.witness];
        }
      }
      if (Object.prototype.hasOwnProperty.call(standoffData, 'combined_gap_before')) {
        if (parent.text.length > 0) {
          parent.text[0].combined_gap_before = [];
        }
        if (Object.prototype.hasOwnProperty.call(parent, 'combined_gap_before_subreadings')) {
          if (parent.combined_gap_before_subreadings.indexOf(standoffData.witness) === -1) {
            parent.combined_gap_before_subreadings.push(standoffData.witness);
          }
        } else {
          parent.combined_gap_before_subreadings = [standoffData.witness];
        }
        if (!Object.prototype.hasOwnProperty.call(parent, 'combined_gap_before_subreadings_details')) {
          parent.combined_gap_before_subreadings_details = {};
        }
        //even if we have it already overwrite because should be the same data
        parent.combined_gap_before_subreadings_details[standoffData.witness] = standoffData.combined_gap_before_details;
      }
    },



    /** This deletes any entries from the standoff marked_readings that were not applied in the last pass
     * and deletes the applied key from all standoff marked_readings so that is clean for the next pass
     * (entries cease to apply when units change length or readings move etc.)
     * This is also sensitive to find_subreadings being called on a single unit in which case only
     * unused marked readings belonging to that unit should be deleted
     * */
    _cleanStandoffMarking: function (appId, unitId) {
      let unit;
      if (typeof appId !== 'undefined' && typeof unitId !== 'undefined') {
        unit = CL.findUnitById(appId, unitId);
      }
      for (const key in CL.data.marked_readings) {
        if (Object.prototype.hasOwnProperty.call(CL.data.marked_readings, key)) {
          for (let i = 0; i < CL.data.marked_readings[key].length; i += 1) {
            if (typeof unit === 'undefined' || (CL.data.marked_readings[key][i].start === unit.start &&
              CL.data.marked_readings[key][i].end === unit.end &&
              CL.data.marked_readings[key][i].apparatus === appId)) {

              if (Object.prototype.hasOwnProperty.call(CL.data.marked_readings[key][i], 'applied')) {
                delete CL.data.marked_readings[key][i].applied;
              } else {
                CL.data.marked_readings[key][i] = null;
              }
            }
          }
          CL.removeNullItems(CL.data.marked_readings[key]);
          if (CL.data.marked_readings[key].length === 0) {
            delete CL.data.marked_readings[key];
          }
        }
      }
    },

    /** removes supplied data from the main reading */
    _removeFromMainReading: function (list) {
      var token, reading, witness, index, witnesses;
      for (let i = 0; i < list.length; i += 1) {
        witness = list[i][0];
        reading = list[i][1];
        if (reading.witnesses.indexOf(witness) !== -1) {
          witnesses = reading.witnesses.slice();
          witnesses.splice(witnesses.indexOf(witness), 1);
          reading.witnesses = witnesses;
        }
        for (let j = 0; j < reading.text.length; j += 1) {
          token = reading.text[j];
          index = token.reading.indexOf(witness);
          if (index !== -1) {
            token.reading.splice(index, 1);
          }
          delete token[witness];
        }
      }
    },

    _findChildReading: function (unit, standoffReading) {
      if (_test) {
        console.log('this one');
        console.log(JSON.parse(JSON.stringify(unit)));
      }
      for (let i = 0; i < unit.readings.length; i += 1) {
        if (_test) {
          console.log(i);
          console.log(JSON.parse(JSON.stringify(unit.readings[i])));
        }
        //if our target witness is in this reading
        if (unit.readings[i].witnesses.indexOf(standoffReading.witness) !== -1) {
          if (_test) {
            console.log('here');
            console.log(CL.extractWitnessText(unit.readings[i], {
              'witness': standoffReading.witness,
              'reading_type': 'subreading'
            }));
            console.log(standoffReading.reading_text);
          }
          if (standoffReading.reading_text === CL.extractWitnessText(unit.readings[i], {
            'witness': standoffReading.witness,
            'reading_type': 'subreading'
          })) {
            return [unit.readings[i], i];
          }
        } else if (Object.prototype.hasOwnProperty.call(unit.readings[i], 'subreadings')) {
          for (const key in unit.readings[i].subreadings) {
            if (Object.prototype.hasOwnProperty.call(unit.readings[i].subreadings, key)) {
              for (let j = 0; j < unit.readings[i].subreadings[key].length; j += 1) {
                if (unit.readings[i].subreadings[key][j].witnesses.indexOf(standoffReading.witness) !== -1) {
                  if (standoffReading.reading_text === CL.extractWitnessText(unit.readings[i], {
                    'witness': standoffReading.witness,
                    'reading_type': 'subreading'
                  })) {
                    return [unit.readings[i], i];
                  }
                }
              }
            }
          }
        }
      }
      return [null, -1];
    },

    _isSeparatedReading: function (appId, unitId, witness) {
      if (!Object.prototype.hasOwnProperty.call(CL.data, 'separated_witnesses')) {
        return [false];
      }
      for (let i = 0; i < CL.data.separated_witnesses.length; i += 1) {
        if (appId === CL.data.separated_witnesses[i].app_id && unitId === CL.data.separated_witnesses[i].unit_id) {
          if (CL.data.separated_witnesses[i].witnesses.indexOf(witness) !== -1) {
            return [true, JSON.parse(JSON.stringify(CL.data.separated_witnesses[i].witnesses))];
          }
        }
      }
      return [false];
    },

    /** we want this to find genuine readings so never give extractWitnessText the unit id otherwise it will
    * find non-existent readings */
    _findParentReading: function (unit, appId, standoffReading, createParent, createPosition) {
      var readings, separatedWitnesses, temp;
      readings = [];
      if (_test) {
        console.log('looking for a match to this');
        console.log(standoffReading.parent_text);
        console.log('in');
      }
      for (let i = 0; i < unit.readings.length; i += 1) {
        if (_test) {
          console.log(CL.extractWitnessText(unit.readings[i], undefined, _test));
        }
        if (CL.extractWitnessText(unit.readings[i]) === standoffReading.parent_text) {
          readings.push(unit.readings[i]);
        }
      }
      if (_test) {
        console.log(readings);
      }
      if (readings.length === 1) {
        return readings[0];
      }
      if (readings.length > 0) {
        temp = SR._isSeparatedReading(appId, unit._id, standoffReading.witness);
        if (temp[0]) {
          temp[1].splice(temp[1].indexOf(standoffReading.witness, 1));
          for (let i = 0; i < readings.length; i += 1) {
            separatedWitnesses = CL.getAllReadingWitnesses(readings[i]);
            if (temp[1].length > 0 && separatedWitnesses.indexOf(temp[1][0]) !== -1) {
              return readings[i];
            }
          }
        }
        // else always chose the first we found because it should always be the main reading for
        // that set (any split offs will be put after the main one)
        return readings[0];
      }
      if (createParent === true) {
        if (_test) {
          console.log('creating new parent');
        }
        if (Object.prototype.hasOwnProperty.call(standoffReading, 'om_details')) {
          CL.createNewReading(unit, 'gap', standoffReading.om_details, createPosition);
        } else if (standoffReading.parent_text === 'om.' ||
          CL.project.omCategories.indexOf(standoffReading.parent_text) != -1) {
          CL.createNewReading(unit, 'om', undefined, createPosition);
        } else {
          CL.createNewReading(unit, 'other', standoffReading.parent_text, createPosition);
        }
        for (let i = 0; i < unit.readings.length; i += 1) {
          if (CL.extractWitnessText(unit.readings[i]) === standoffReading.parent_text) {
            return unit.readings[i];
          }
        }
      }
      return null;
    },

    _witnessIn: function (subreadings, witness) {
      for (const key in subreadings) {
        if (Object.prototype.hasOwnProperty.call(subreadings, key)) {
          for (let i = 0; i < subreadings[key].length; i += 1) {
            if (subreadings[key][i].witnesses.indexOf(witness) !== -1) {
              return true;
            }
          }
        }
      }
      return false;
    },

    /** for each witness finds all decision classes that apply to the reading and passes it all
    * on to _addToSubreadings */
    _makeSubreadings: function (reading, ruleClasses) {
      let token, witness, subreadings, decisionClass, identList, combinedGapBefore, combinedGapAfter, options;
      if (typeof ruleClasses === 'undefined') {
        ruleClasses = CL.getRuleClasses(undefined, undefined, 'value', ['identifier', 'subreading']);
      }
      subreadings = {};
      const forDeletion = [];
      for (let i = 0; i < reading.witnesses.length; i += 1) {
        combinedGapBefore = undefined;
        combinedGapAfter = undefined;
        witness = reading.witnesses[i];
        identList = [];
        for (let j = 0; j < reading.text.length; j += 1) {
          token = reading.text[j];
          if (Object.prototype.hasOwnProperty.call(token, witness)) {
            if (Object.prototype.hasOwnProperty.call(token[witness], 'decision_class')) {
              decisionClass = token[witness].decision_class;
              for (let k = 0; k < decisionClass.length; k += 1) {
                if (identList.indexOf(decisionClass[k]) === -1 &&
                  Object.prototype.hasOwnProperty.call(ruleClasses, decisionClass[k])) {
                  identList.push(decisionClass[k]);
                }
              }
            }
          }
        }
        if (Object.prototype.hasOwnProperty.call(reading, 'combined_gap_before_subreadings') &&
          reading.combined_gap_before_subreadings.indexOf(witness) !== -1) {
          combinedGapBefore = [];
        }
        if (Object.prototype.hasOwnProperty.call(reading, 'combined_gap_after_subreadings') &&
          reading.combined_gap_after_subreadings.indexOf(witness) !== -1) {
          combinedGapAfter = [];
        }
        if (identList.length > 0) {
          identList.sort();
          options = {};
          if (typeof ruleClasses !== 'undefined') {
            options.rules = ruleClasses;
          }
          if (typeof combinedGapBefore !== 'undefined') {
            options.combined_gap_before = combinedGapBefore;
          }
          if (typeof combinedGapAfter !== 'undefined') {
            options.combined_gap_after = combinedGapAfter;
          }
          if (_test) {
            console.log(JSON.parse(JSON.stringify(identList)));
            console.log(JSON.parse(JSON.stringify(subreadings)));
            console.log(JSON.parse(JSON.stringify(reading)));
          }
          subreadings = SR._addToSubreadings(subreadings, reading, witness, identList, options);
          if (!$.isEmptyObject(subreadings)) {
            reading.subreadings = subreadings;
            forDeletion.push([witness, reading]);
          }
        }
      }
      SR._removeFromMainReading(forDeletion);
      return reading;
    },

    /**
   * adds a new subreading to the subreading dictionary supplied
   * @param {Object} subreadings - the current dictionary of subreadings (or an empty object if this parent doesn't
   *                               have any)
   * @param {Object} reading - the reading which needs to be made into a subreading
   * @param {String} witness - the witness that is becoming the subreading
   * @param {Array} typeList - a list of abbreviation type labels to be applied to the new subreading
   * @param {Object} options - other optional data provided which are: 	
   *                                rules - a list of the regularisation rules that are relevant for creating the subreadings
   * 									              text - the text of the subreading being created
   * 									              combined_gap_before - boolean
   * 									              combined_gap_after - boolean
   * 									              combined_gap_before_details - string
   * 									              standoff - boolean
   * */
    _addToSubreadings: function (subreadings, reading, witness, typeList, options) {
      var matchFound, textString, type, realSuffixList, fakeSuffixList, suffixString, target;
      if (typeof options === 'undefined') {
        options = {};
      }
      if (typeof options.rules === 'undefined') {
        options.rules = CL.getRuleClasses(undefined, undefined, 'value', ['identifier', 'subreading']);
      }
      //target is the reading at the object level where two of the keys are witnesses and text
      target = CL.getSubreadingOfWitness(reading, witness, true);
      if (target === null) {
        target = reading;
      }
      if (options.combined_gap_before) {
        target.text[0].combined_gap_before = [];
      }
      if (options.combined_gap_before_details) {
        target.text[0].combined_gap_before_details = options.combined_gap_before_details;
      }
      if (options.combined_gap_after) {
        target.text[target.text.length - 1].combined_gap_after = [];
      }
      // make the suffix
      // the suffix is split into real and fake, real being those that will end up as subreadings in the apparatus
      // and fake being all other subreadings
      realSuffixList = [];
      fakeSuffixList = [];
      for (let i = 0; i < typeList.length; i += 1) {
        if (!Object.prototype.hasOwnProperty.call(options.rules, typeList[i])) {
          typeList[i] = null;
          continue;
        }
        if (typeof options.rules[typeList[i]][0] === 'undefined') {
          suffixString = '-';
        } else {
          suffixString = options.rules[typeList[i]][0];
        }
        if (options.rules[typeList[i]][1]) {
          if (realSuffixList.indexOf(suffixString) === -1) {
            realSuffixList.push(suffixString);
          }
        } else {
          if (fakeSuffixList.indexOf(suffixString) === -1) {
            fakeSuffixList.push(suffixString);
          }
        }
      }
      CL.removeNullItems(typeList);
      realSuffixList.sort();
      fakeSuffixList.sort();
      // add parenthesis to the fake suffixes
      if (fakeSuffixList.length > 0) {
        fakeSuffixList.splice(0, 0, '(');
        fakeSuffixList.push(')');
        realSuffixList.push.apply(realSuffixList, fakeSuffixList);
      }
      type = typeList.join('|');
      // extract the witness text and check we only have one instance of each text
      if (type.length > 0) {
        if (Object.prototype.hasOwnProperty.call(subreadings, type)) {
          if (typeof options.text !== 'undefined') {
            textString = options.text;
          } else {
            textString = CL.extractWitnessText(target, {
              'witness': witness,
              'reading_type': 'subreading',
              'required_rules': typeList
            });
          }
          if (textString === '') {
            if (Object.prototype.hasOwnProperty.call(target, 'type') && target.type === 'om') {
              textString = 'om.';
            } else if (Object.prototype.hasOwnProperty.call(target, 'type') && target.type === 'lac') {
              if (Object.prototype.hasOwnProperty.call(target, 'details')) {
                textString = target.details;
              }
            }
          }

          matchFound = false;
          for (let i = 0; i < subreadings[type].length; i += 1) {
            if (subreadings[type][i].text_string === textString ||
              '&lt;' + subreadings[type][i].text_string + '&gt;' === textString) {
              if (subreadings[type][i].witnesses.indexOf(witness) === -1) {
                subreadings[type][i].witnesses.push(witness);
                for (let j = 0; j < subreadings[type][i].text.length; j += 1) {
                  subreadings[type][i].text[j].reading.push(witness);
                  // the next if statement stops errors if the target has a different length text list.
                  // that should only happen if there are stacked regularisations made in SV and the reading 
                  // is not unique in the subreadings. It was added to fix a but where om was regularised to an extant
                  // word (with a category not shown in OR) and then that word was regularised to another reading 
                  // (which is shown in OR). In this case the target had an empty text list but when only displaying
                  // edition subreadings the text of the first regularisation matched it to an existing subreading.
                  if (target.text.length > j) {
                    subreadings[type][i].text[j][witness] = target.text[j][witness];
                    if (Object.prototype.hasOwnProperty.call(options, 'standoff') && options.standoff === true) {
                      subreadings[type][i].text[j][witness]['interface'] = target.text[j]['interface'];
                    }
                  }
                }
              }
              matchFound = true;
              break;
            }
          }
          if (matchFound === false) {
            subreadings = SR._addNewSubreading(subreadings, target, witness, type, realSuffixList.join(''),
              options.text, typeList);
          }
        } else {
          subreadings[type] = [];
          subreadings = SR._addNewSubreading(subreadings, target, witness, type, realSuffixList.join(''),
            options.text, typeList);
        }
      }
      return subreadings;
    },

    _addNewSubreading: function (subreadings, reading, witness, type, suffix, text, requiredRules) {
      let newToken, textString;
      if (reading.text.length > 0) {
        if (typeof text !== 'undefined') {
          textString = text;
        } else {
          textString = CL.extractWitnessText(reading, {
            'witness': witness,
            'reading_type': 'subreading',
            'required_rules': requiredRules
          });
        }
        if (_test) {
          console.log(textString);
        }
      } else {
        if (Object.prototype.hasOwnProperty.call(reading, 'details')) {
          textString = reading.details;
        } else {
          textString = 'om.';
        }
      }
      const newEntry = {
        'text': [],
        'text_string': textString,
        'witnesses': [witness],
        'suffix': suffix
      };
      if (Object.prototype.hasOwnProperty.call(reading, 'type')) {
        newEntry.type = reading.type;
      }
      if (Object.prototype.hasOwnProperty.call(reading, 'details')) {
        newEntry.details = reading.details;
      }
      for (let i = 0; i < reading.text.length; i += 1) {
        newToken = {};
        newToken.index = reading.text[i].index;
        newToken.verse = reading.text[i].verse;
        newToken[witness] = reading.text[i][witness];
        // If this token has a decision applied then get the t (as we are after the subreading)
        if (Object.prototype.hasOwnProperty.call(reading.text[i], 'decision_details')) {
          // TODO: is the 0 right? what happens with chaining!!! also check extract_witness_text and other places with
          // this structure
          newToken['interface'] = reading.text[i].decision_details[0].t;
        } else {
          newToken['interface'] = reading.text[i]['interface'];
        }
        newToken.reading = [witness];
        if (Object.prototype.hasOwnProperty.call(reading.text[i], 'was_gap')) {
          newToken.was_gap = reading.text[i].was_gap;
        }
        newEntry.text.push(newToken);
      }
      subreadings[type].push(newEntry);
      return subreadings;
    },

    _stripExtraWitnessDetailsFromTextList: function (text, witness) {
      for (let i = 0; i < text.length; i += 1) {
        for (let j = 0; j < text[i].reading.length; j += 1) {
          if (text[i].reading[j] !== witness) {
            delete text[i][text[i].reading[j]];
            text[i].reading[j] = null;
          }
        }
        text[i].reading = CL.removeNullItems(text[i].reading);
      }
      return text;
    },

    _doLoseSubreadings: function (reading) {
      let witness, token, text;
      const parentLength = reading.text.length;
      for (const type in reading.subreadings) { //loop through subreading types
        if (Object.prototype.hasOwnProperty.call(reading.subreadings, type)) {
          for (let i = 0; i < reading.subreadings[type].length; i += 1) { //loop through all the subreading of that type
            for (let j = 0; j < reading.subreadings[type][i].witnesses.length; j += 1) {
              witness = reading.subreadings[type][i].witnesses[j];
              reading.witnesses.push(witness);

              if (reading.subreadings[type][i].text.length == parentLength && //we shouldn't need this first condition
                ((!Object.prototype.hasOwnProperty.call(reading, 'standoff_subreadings') ||
                  reading.standoff_subreadings.indexOf(witness) === -1))) {
                for (let k = 0; k < reading.subreadings[type][i].text.length; k += 1) {
                  token = reading.subreadings[type][i].text[k];
                  reading.text[k].reading.push(token.reading[token.reading.indexOf(witness)]);
                  reading.text[k][witness] = reading.subreadings[type][i].text[k][witness];
                }
              } else { // this is a standoff reading so SR_text must be employed
                if (!Object.prototype.hasOwnProperty.call(reading, 'SR_text')) {
                  reading.SR_text = {};
                }
                //remove the extra readings from each word, siglum and reading
                text = SR._stripExtraWitnessDetailsFromTextList(JSON.parse(JSON.stringify(reading.subreadings[type][i].text)), witness);
                if (!Object.prototype.hasOwnProperty.call(reading.SR_text, witness)) {
                  reading.SR_text[witness] = {
                    'text': text
                  };
                  for (let k = 0; k < reading.SR_text[witness].text.length; k += 1) {
                    if (Object.prototype.hasOwnProperty.call(reading.SR_text[witness].text[k][witness], 'decision_details')) {
                      reading.SR_text[witness].text[k]['interface'] = reading.SR_text[witness].text[k][witness].decision_details[0].t;
                    } else {
                      if (Object.prototype.hasOwnProperty.call(reading.SR_text[witness].text[k], 't')) {
                        reading.SR_text[witness].text[k]['interface'] = reading.SR_text[witness].text[k].t;
                      } else {
                        if (reading.SR_text[witness].text[k][witness]['interface'] === undefined) {
                          // reading.SR_text[witness].text[k]['interface'] = reading.SR_text[witness].text[k]['interface'];
                          reading.SR_text[witness].text[k][witness]['interface'] = reading.SR_text[witness].text[k]['interface'];
                        } else {
                          reading.SR_text[witness].text[k]['interface'] = reading.SR_text[witness].text[k][witness]['interface'];
                        }
                      }
                    }
                  }
                  if (Object.prototype.hasOwnProperty.call(reading.subreadings[type][i], 'type')) {
                    reading.SR_text[witness].type = reading.subreadings[type][i].type;
                  }
                  if (Object.prototype.hasOwnProperty.call(reading.subreadings[type][i], 'details')) {
                    reading.SR_text[witness].details = reading.subreadings[type][i].details;
                  }
                }
                if (Object.prototype.hasOwnProperty.call(reading, 'standoff_subreadings')) {
                  reading.standoff_subreadings.splice(reading.standoff_subreadings.indexOf(witness), 1);
                  if (reading.standoff_subreadings.length === 0) {
                    delete reading.standoff_subreadings;
                  }
                }
              }
            }
          }
        }
      }
      reading.witnesses = CL.setList(reading.witnesses);
      delete reading.subreadings;
    }

  };

}());
