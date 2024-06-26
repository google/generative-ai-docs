/**
 * Copyright 2023 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// Used in the prompts to indicate the boundary between a prefix and its corresponding value
// NOTE: The prefix delimiter should not occur anywhere in the example value that follows a prefix
export const PREFIX_DELIMITER = ':'

export const constructPrompt = (promptComponents, inputs) => {
  const lines = []
  if (promptComponents.preamble) {
    lines.push(promptComponents.preamble)
  }
  let currentPrefixIndex
  ;[...promptComponents.examples, inputs].forEach(values => {
    for (let i = 0; i < values.length; i++) {
      const prefix = promptComponents.prefixes[i]
      const value = values[i]
      if (prefix) {
        lines.push(`${prefix} ${value}`)
      } else {
        lines.push(value)
      }
      currentPrefixIndex = i
    }
  })
  if (currentPrefixIndex < promptComponents.prefixes.length - 1) {
    const nextPrefix = promptComponents.prefixes[currentPrefixIndex + 1]
    if (nextPrefix) {
      lines.push(nextPrefix)
    }
  }
  return lines.join('\n')
}

export const SIMILE_PROMPT_COMPONENTS = {
  preamble:
    'A good simile contains a concrete image that illustrates the concept we want to convey without being too obvious. Good similes are unexpected and evocative. Below are some examples of good similes.',
  prefixes: [
    `Here is a concept${PREFIX_DELIMITER}`,
    `Here is a simile that illustrates it${PREFIX_DELIMITER}`
  ],
  examples: [
    [
      'a helping hand',
      "I just come around to help like Batman's utility belt."
    ],
    [
      'pizza',
      'Pizza is like a symphony of flavors, with each ingredient representing note in a complex harmony that dances across the tongue.'
    ],
    [
      'struggling through life',
      'Life is like making a diamond—finding treasure in the pressure and doing a whole lot of shaping and shining.'
    ],
    [
      'silence',
      'The silence was like a deep, still pool of water, reflecting nothing but its own serene emptiness, yet hiding unfathomable truths beneath its surface.'
    ],
    [
      'a long-distance relationship ',
      "A long-distance relationship is like playing tennis against a wall. It's doable, but pales in comparison to having an in-person companion."
    ],
    [
      'something going differently than you anticipated',
      'The unexpected turn of events was like a sudden gust of wind inside a Buddhist temple, scattering the grains of the meticulously arranged sand mandala that was my future.'
    ],
    [
      'pretending',
      'Pretending was like an elaborate dance—even when the steps were rehearsed to perfection, the rhythm always felt slightly off, and the movements lacked the elusive grace that comes from spontaneous expression.'
    ],
    [
      'a croaky voice',
      "The man's voice was like a rusty hinge that had not been oiled for years, emitting a groan of protest with every movement."
    ],
    [
      'notoriety is short-lived',
      'Glory is like a circle in the water, which never ceases to enlarge itself until it expands endlessly into nothing.'
    ],
    [
      'a drizzle',
      'The rain was like a delicate veil, casting a misty shroud over the familiar landscape, lending an air of mystery to the mundane.'
    ],
    [
      'exhaustion',
      'Every step I took felt like wading through molasses, and the even slightest exertions left me gasping for breath.'
    ],
    [
      'unpleasant memories',
      'Like a cloud of noxious fumes, the memories suffused every waking moment with their acrid stench, obscuring the present and casting a shadow over the future.'
    ],
    [
      'something bothering you',
      'It was like a loose thread on a sweater, inconspicuous but insistent, tugging at the fabric of my psyche until it finally threatened to unravel everything.'
    ],
    [
      'a beautiful lady',
      "Her beauty hangs upon the cheek of night, like a rich jewel in an Ethiop's ear."
    ]
  ]
}

export const EXPLODE_PROMPT_COMPONENTS = {
  preamble:
    'A same-sounding phrase is a phrase that sounds like another word or phrase.',
  prefixes: ['Here is a same-sounding phrase for the word', ''],
  examples: [
    [`"defeat"${PREFIX_DELIMITER}`, 'da feet (as in "the" feet)'],
    [`"defeat"${PREFIX_DELIMITER}`, "deaf eat (can't hear while eating)"],
    [
      `"surprise"${PREFIX_DELIMITER}`,
      'Sir Prize (a knight whose name is Prize)'
    ],
    [
      `"surprise"${PREFIX_DELIMITER}`,
      'serf prize (award given to a feudal laborer)'
    ],
    [`"weapon"${PREFIX_DELIMITER}`, 'weep on (to cry on)'],
    [`"weapon"${PREFIX_DELIMITER}`, 'wee pawn (a tiny chess piece)'],
    [`"stabilize"${PREFIX_DELIMITER}`, 'stable eyes (a steady gaze)'],
    [
      `"adoration"${PREFIX_DELIMITER}`,
      'add oration (to include a formal speech)'
    ],
    [
      `"ridiculous"${PREFIX_DELIMITER}`,
      'ridicule us (to shame us collectively)'
    ],
    [`"ridiculous"${PREFIX_DELIMITER}`, 'ridicule less (to be less scornful)'],
    [
      `"sensation"${PREFIX_DELIMITER}`,
      'sensei shun (to avoid your martial arts teacher)'
    ],
    [
      `"sensation"${PREFIX_DELIMITER}`,
      'sin say shun (to admit your sins and become a pariah)'
    ],
    [
      `"recognize"${PREFIX_DELIMITER}`,
      "wreck on eyes (so visually outrageous that it's painful)"
    ],
    [
      `"recognize"${PREFIX_DELIMITER}`,
      'wreck on ice (to wipe out on a frozen pond)'
    ],
    [
      `"recognize"${PREFIX_DELIMITER}`,
      're-cognize (to fix broken gears in a clock)'
    ],
    [
      `"American"${PREFIX_DELIMITER}`,
      "I'm arrogant (self-admission of haughtiness)"
    ],
    [
      `"American"${PREFIX_DELIMITER}`,
      'aim Eric can (Eric is a skilled marksman)'
    ],
    [
      `"recollection"${PREFIX_DELIMITER}`,
      'wreck collection (cleanup after a traffic accident)'
    ],
    [`"euthanasia"${PREFIX_DELIMITER}`, 'youth in Asia (youngsters in Asia)'],
    [
      `"depend"${PREFIX_DELIMITER}`,
      'deep end (deep section of a swimming pool)'
    ],
    [
      `"gemini"${PREFIX_DELIMITER}`,
      'gem in eye (a precious stone lodged in the cornea)'
    ],
    [`"example"${PREFIX_DELIMITER}`, 'egg sample (a trial tasting of an egg)'],
    [
      `"initiate"${PREFIX_DELIMITER}`,
      'and then she ate (and she subsequently ate)'
    ],
    [
      `"innuendo"${PREFIX_DELIMITER}`,
      'in your window (perched on your windowsill)'
    ],
    [`"moustache"${PREFIX_DELIMITER}`, 'must ask (need to inquire)'],
    [`"mystery"${PREFIX_DELIMITER}`, 'missed hurry (overlooked haste)'],
    [
      `"expressway"${PREFIX_DELIMITER}`,
      'express whey (a speedy delivery of milk byproduct)'
    ],
    [
      `"expressway"${PREFIX_DELIMITER}`,
      'express sway (to demonstrate influence)'
    ],
    [
      `"expressway"${PREFIX_DELIMITER}`,
      'ex-press way (a path without news media)'
    ],
    [
      `"committed"${PREFIX_DELIMITER}`,
      'come mitted (to show up in boxing gloves, ready to fight)'
    ],
    [`"committed"${PREFIX_DELIMITER}`, 'comet kid (an aspiring astronaut)'],
    [`"mismanaged"${PREFIX_DELIMITER}`, 'mess-managed (overseen by a mess)'],
    [`"topics"${PREFIX_DELIMITER}`, 'top picks (best selections)'],
    [`"topics"${PREFIX_DELIMITER}`, 'two pics (two pictures)'],
    [`"defender"${PREFIX_DELIMITER}`, 'defend her (protect her)'],
    [
      `"extraordinary"${PREFIX_DELIMITER}`,
      'X-ray or dairy? (a choice between radiology or milk)'
    ],
    [
      `"capitalize"${PREFIX_DELIMITER}`,
      'capital eyes (honed-in on financial assets)'
    ],
    [
      `"capitalize"${PREFIX_DELIMITER}`,
      "capital lies (misinformation from the country's administrative center)"
    ],
    [
      `"provoking"${PREFIX_DELIMITER}`,
      'pro-vogue king (a monarch in support of voguing)'
    ],
    [`"provoking"${PREFIX_DELIMITER}`, 'provoke king (a master antagonizer)'],
    [`"Tibet"${PREFIX_DELIMITER}`, 'tie bet (an evenly matched wager)'],
    [`"Tibet"${PREFIX_DELIMITER}`, 'Thai bat (a bat from Thailand)'],
    [`"immediate"${PREFIX_DELIMITER}`, 'I mediate (I intervene)'],
    [
      `"immediate"${PREFIX_DELIMITER}`,
      'Imma date it (as in "I\'m going to write today\'s date on it")'
    ],
    [`"paper"${PREFIX_DELIMITER}`, 'pay peer (to give a friend money)'],
    [`"paper"${PREFIX_DELIMITER}`, 'pa pure (dad is clean)'],
    [`"beer"${PREFIX_DELIMITER}`, 'be here (to be present)'],
    [
      `"secondary"${PREFIX_DELIMITER}`,
      'sickened dairy (milk that has gone bad)'
    ],
    [
      `"secondary"${PREFIX_DELIMITER}`,
      'seek a deary (to search for a grandchild)'
    ],
    [
      `"occasion"${PREFIX_DELIMITER}`,
      'oak case in (to box something in with oak wood)'
    ],
    [
      `"automatic"${PREFIX_DELIMITER}`,
      'auto Matt sick (Matt instantly becomes ill)'
    ]
  ]
}

export const UNEXPECT_PROMPT_COMPONENTS = {
  preamble:
    'For each scene below, we provide an example of how you can incorporate additional details to give that scene an unexpected twist.',
  prefixes: [
    `Here is a scene${PREFIX_DELIMITER}`,
    `Here is an unexpected twist${PREFIX_DELIMITER}`
  ],
  examples: [
    ['rapping', 'rapping in morse code'],
    [
      'a parking ticket',
      'a parking ticket that is written in Sanskrit and folded into an origami swan'
    ],
    ['snorkeling', 'snorkeling in a massive bathtub filled with champagne'],
    [
      'a door',
      'a door that only opens when you sing the national anthem of Equatorial Guinea'
    ],
    ['grinding a skateboard', 'grinding a skateboard on Titanic railings'],
    [
      'eating ramen',
      'eating ramen with chopsticks that are made out of icicles'
    ],
    [
      'painting a mural',
      'painting a mural on the ceiling of a commercial airliner'
    ],
    [
      'playing piano',
      'playing piano in the middle of the mosh pit at a metal concert'
    ],
    ['a church', 'a church that is made out of Jenga blocks'],
    ['sleeping', 'sleeping in a hammock that is tied between two stop signs'],
    ['a Bonsai tree', 'a Bonsai tree that is made out of broccoli'],
    [
      'playing soccer',
      'playing soccer with a bowling ball on a field that is made out of Lego bricks'
    ]
  ]
}

export const CHAIN_PROMPT_COMPONENTS = {
  preamble:
    'A word chain is a sequence of eight words where each word in the sequence is semantically related to the word that precedes it.',
  prefixes: ['Here is an example of a word chain beginning with', ''],
  examples: [
    [
      `"fresh"${PREFIX_DELIMITER}`,
      'fresh, fruit, orange, juice, blender, kitchen, chef, kiss'
    ],
    [
      `"bat"${PREFIX_DELIMITER}`,
      'bat, ball, baseball, field, hill, mountain, cave, stalactite'
    ],
    [
      `"run"${PREFIX_DELIMITER}`,
      'run, exercise, muscle, strength, power, voltage, current, affairs'
    ],
    [
      `"rise"${PREFIX_DELIMITER}`,
      'rise, sun, flower, soil, farm, wheat, dough, cookie'
    ],
    [
      `"oil"${PREFIX_DELIMITER}`,
      'oil, barrel, trade, war, peace, treaty, sign, pen'
    ],
    [
      `"light"${PREFIX_DELIMITER}`,
      'light, feather, bird, nest, home, sweet, candy, corn'
    ],
    [
      `"wave"${PREFIX_DELIMITER}`,
      'wave, ocean, beach, sand, castle, royalty, flag, pole'
    ],
    [
      `"letter"${PREFIX_DELIMITER}`,
      'letter, write, read, book, library, school, cafeteria, lunch lady'
    ],
    [
      `"joystick"${PREFIX_DELIMITER}`,
      'joystick, video game, fun, happy, smile, teeth, shark, tank'
    ],
    [
      `"soul"${PREFIX_DELIMITER}`,
      'soul, body, heart, beat, dance, floor, shoe, sole'
    ],
    [
      `"slow-mo"${PREFIX_DELIMITER}`,
      'slow-mo, capture, cage, bird, sing, voice, speech, podium'
    ],
    [
      `"mini golf"${PREFIX_DELIMITER}`,
      'mini golf, hole, ground, dirt, shovel, snow, ice, cube'
    ]
  ]
}

export const POV_PROMPT_COMPONENTS = {
  preamble:
    'A "hot take" is a perspective that is novel and thought-provoking. Some hot takes are lighthearted and humorous, while others may be provocative or polarizing.',
  prefixes: ['Here are some hot takes about', ''],
  examples: [
    [
      `fast food${PREFIX_DELIMITER}`,
      [
        'Fast food is a game of Russian roulette with your taste buds and digestive system.',
        'Fast food really lets you choose your own adventure, with endless combinations of toppings, sides, and sauces to customize your meal.',
        'Fast food is the ultimate ""pick-me-up""—until you realize you\'ve picked up a few extra pounds.',
        'Fast food restaurants are the ultimate equalizer, where everyone from millionaires to broke college students can enjoy the same greasy goodness.'
      ].join('\n')
    ],
    [
      `mythology${PREFIX_DELIMITER}`,
      [
        'Mythology is a treasure trove of dad jokes.',
        'Mythology is the original fan fiction—except the fans were ancient civilizations.',
        'The gods of mythology are basically just humans with PR teams and superpowers.',
        "Mythology was just ancient peoples' way of explaining the world around them—now we have science for that."
      ].join('\n')
    ],
    [
      `gummy bears${PREFIX_DELIMITER}`,
      [
        'Gummy bears are the perfect snack for people who like to chew their food into submission.',
        "Gummy bears are healthy because they're just fruit mixed with some gelatin.",
        "Gummy bears are the M&Ms of the gummy world, except they don't melt in your hand (or your mouth).",
        "Gummy bears aren't worth the calories."
      ].join('\n')
    ],
    [
      `cell phones${PREFIX_DELIMITER}`,
      [
        'Cell phones have turned people into terrible listeners.',
        'Cell phones are a great way to cheat on math tests.',
        'Cell phones have revolutionized the way we think about dating and romance.',
        'Cell phones are a tactic employed by the government to surveil you.'
      ].join('\n')
    ],
    [
      `GMOs${PREFIX_DELIMITER}`,
      [
        'GMOs are the product of bored scientists who need a new hobby.',
        "GMOs have spoiled the public's perception of what an average tomato looks like.",
        'GMOs are the love child of nature and technology.',
        'GMOs will result in a generation of people with mutant powers.'
      ].join('\n')
    ]
  ]
}

export const ALLITERATION_PROMPT_COMPONENTS = {
  preamble: '',
  prefixes: [
    `Here is a topic${PREFIX_DELIMITER}`,
    'Here are some examples of words that are related to that topic and start with the letter(s)',
    ''
  ],
  examples: [
    [
      'music terminology',
      `T${PREFIX_DELIMITER}`,
      'tempo, tune, tone, treble, timbre, tablature, triad, tremolo, track, toccata, trill'
    ],
    [
      'languages',
      `G${PREFIX_DELIMITER}`,
      'German, Greek, Gaelic, Georgian, Gujarati, Greenlandic, Gullah, Gikuyu'
    ],
    [
      'culinary techniques',
      `B${PREFIX_DELIMITER}`,
      'bake, boil, broil, braise, blanch, barbecue'
    ],
    [
      'household items',
      `I${PREFIX_DELIMITER}`,
      'iron, incense, insulation, inflatable mattress, ice cube tray, ice cream scoop, immersion blender'
    ],
    [
      'well-known cities',
      `M${PREFIX_DELIMITER}`,
      'Madrid, Moscow, Mumbai, Melbourne, Manila, Montreal, Munich, Milan, Manchester, Marrakech, Marseille, Medellin'
    ],
    ['palindromes', 'R:', 'racecar, radar, refer, rotator, redder'],
    [
      'things related to archaeology',
      `E${PREFIX_DELIMITER}`,
      'excavation, epigraph, ecofact, ethnography, exhibit'
    ],
    [
      'adjectives for describing animals',
      `D${PREFIX_DELIMITER}`,
      'dangerous, docile, deft, delicate, diurnal, domesticated'
    ],
    ['body parts', 'TH:', 'thumb, throat, thigh, thyroid, thalamus'],
    [
      'names of plants',
      `F or PH${PREFIX_DELIMITER}`,
      'fern, fuchsia, fiddle-leaf fig, philodendron, phlox'
    ]
  ]
}

export const ACRONYM_PROMPT_COMPONENTS = {
  preamble:
    'An acronym is an abbreviation of several words in such a way that the abbreviation itself forms a pronounceable word.',
  prefixes: ['Here is an acronym that uses the letters of the word', ''],
  examples: [
    [`"rap"${PREFIX_DELIMITER}`, 'RAP - Recognizing Analogous Patterns'],
    [
      `"mural"${PREFIX_DELIMITER}`,
      'MURAL - Magnifying Urban Realities Affecting Lives '
    ],
    [`"wow"${PREFIX_DELIMITER}`, 'WOW - Walking On Water'],
    [`"happy"${PREFIX_DELIMITER}`, 'HAPPY - Having A Purpose Promises Youth'],
    [
      `"weapon"${PREFIX_DELIMITER}`,
      'WEAPON - Wieldable Equipment for Aggressive Purposes Or Neutralization'
    ],
    [
      `"hope"${PREFIX_DELIMITER}`,
      'HOPE - Holding Optimistic Possibilities Endlessly'
    ],
    [
      `"youth"${PREFIX_DELIMITER}`,
      'YOUTH - Young Outstanding Unique Trailblazers of Humanity'
    ],
    [`"wave"${PREFIX_DELIMITER}`, 'WAVE - Water Affecting Vital Environments'],
    [`"fly"${PREFIX_DELIMITER}`, 'FLY - Freely Leaving Yesterday'],
    [
      `"acoustic"${PREFIX_DELIMITER}`,
      'ACOUSTIC - Actively Creating Our Unique Sounds To Intoxicate the Crowd'
    ],
    [
      `"murder"${PREFIX_DELIMITER}`,
      "MURDER - Maliciously Undertaken Ruthless Deadly Executioner's Rage"
    ],
    [`"love"${PREFIX_DELIMITER}`, 'LOVE - Living Overtly Via Empathy'],
    [
      `"music"${PREFIX_DELIMITER}`,
      'MUSIC - Making Up Sounds Intuitively and Creatively'
    ],
    [
      `"punk"${PREFIX_DELIMITER}`,
      'PUNK - Passionate Unconventional Non-conformist Kid'
    ],
    [
      `"safety"${PREFIX_DELIMITER}`,
      'SAFETY - Stopping All Fatal Efforts Towards You'
    ],
    [
      `"Kilimanjaro"${PREFIX_DELIMITER}`,
      'KILIMANJARO - Keen Individuals Leading In Marvelous Adventures, Navigating and Journeying Across the Rugged Outdoors'
    ],
    [
      `"forgive"${PREFIX_DELIMITER}`,
      'FORGIVE - Finding Opportunities to Release Grudges, Inspiring Virtue and Empathy'
    ],
    [
      `"cheetahs"${PREFIX_DELIMITER}`,
      'CHEETAHS - Cunning Hunters, Energetic and Efficient with Terrific Agility and High Speeds'
    ],
    [
      `"radio"${PREFIX_DELIMITER}`,
      'RADIO - Receiving Audio Data with Instant Output'
    ],
    [`"win"${PREFIX_DELIMITER}`, 'WIN - Whatever It Takes'],
    [
      `"money"${PREFIX_DELIMITER}`,
      'MONEY - Made Only by Nearly Exploiting Yourself'
    ],
    [
      `"time"${PREFIX_DELIMITER}`,
      'TIME - The Inevitable Memorializer of Events'
    ],
    [
      `"change"${PREFIX_DELIMITER}`,
      'CHANGE - Cultivating Higher Ambitions and New Goals for Evolution'
    ],
    [`"risk"${PREFIX_DELIMITER}`, 'RISK - Reward Is Seldom Known'],
    [`"lyric"${PREFIX_DELIMITER}`, 'LYRIC - Let Your Rhythm Instill Courage'],
    [`"code"${PREFIX_DELIMITER}`, 'CODE - Completely Optimized Data Exchange'],
    [
      `"New York"${PREFIX_DELIMITER}`,
      'NEW YORK - No Evil Within, Your Own Righteous Kingdom'
    ],
    [
      `"tortoise"${PREFIX_DELIMITER}`,
      'TORTOISE - The Old Reptile Takes Ownership of Its Sluggish Existence'
    ],
    [
      `"skateboard"${PREFIX_DELIMITER}`,
      'SKATEBOARD - Sport Known Among Thrill-seekers Everywhere Because Of Adrenaline Rushes Delivered'
    ],
    [
      `"love is blind"${PREFIX_DELIMITER}`,
      'LOVE IS BLIND - Letting Our Vulnerability Expose Imperfections Shows that Beauty Lies In Noticing Differences'
    ],
    [
      `"dumb luck"${PREFIX_DELIMITER}`,
      "DUMB LUCK - Destiny Unleashes Miracles, Bringing Life's Unforeseen Consequences Kindly"
    ],
    [`"yo-yo"${PREFIX_DELIMITER}`, 'YO-YO - Yanking Over Your Orbit'],
    [
      `"mannequin"${PREFIX_DELIMITER}`,
      'MANNEQUIN - Mobile, Adjustable, Nondescript, and Naked Embodiment that Questions Universal Identity Norms'
    ],
    [
      `"Midas touch"${PREFIX_DELIMITER}`,
      'MIDAS TOUCH  - Making It Desirable And Successful Through Original, Unique, and Creative Habits'
    ]
  ]
}

export const FUSE_PROMPT_COMPONENTS = {
  preamble:
    'One way to practice creative thinking is to identify connections between seemingly unrelated things. For each pair of things below, we provide a creative example of something that both things have in common. Each connection is novel and unexpected, rather than an unoriginal technicality.',
  prefixes: [
    `Thing 1${PREFIX_DELIMITER}`,
    `Thing 2${PREFIX_DELIMITER}`,
    `Here is something that Thing 1 and Thing 2 have in common${PREFIX_DELIMITER}`
  ],
  examples: [
    [
      'airplane',
      'grass',
      'Both an airplane and grass defy gravity in their own way—an airplane by flying through the air, and grass by standing tall against the gravitational pull of the Earth.'
    ],
    [
      'book',
      'smoothie',
      'Both a book and a smoothie can provide a sense of escape and transport the user to another world—a smoothie with its tropical flavors and aromas, and a book with its vivid descriptions and imaginative worlds.'
    ],
    [
      'lantern',
      'zebra',
      'Both a lantern and a zebra can be associated with adventure and exploration—a lantern with its use in camping and outdoor activities, and a zebra with its association with the African wilderness and safari expeditions.'
    ],
    [
      'priest',
      'criminal',
      'Both a priest and a criminal can challenge our perceptions of good and evil and illuminate the complexities of human nature—a priest by reminding us of the fallibility of even the most spiritual leaders, and a criminal by forcing us to confront the factors that may lead someone to a life of crime.'
    ],
    [
      'hope',
      'pity',
      'Both hope and pity can be seen as responses to adversity—hope as a way of coping with and overcoming difficult situations, and pity as a way of acknowledging and sympathizing with those who have experienced hardship.'
    ],
    [
      'art',
      'war',
      'Both art and war can be associated with conflict and tension—art with the contrast between light and dark, warm and cool, and war with the tension between adversaries.'
    ],
    [
      'bridge',
      'waterfall',
      'Both a bridge and a waterfall can be symbols of perseverance and endurance—a bridge by its ability to withstand the test of time and the forces of nature, and a waterfall by its constant flow over time.'
    ],
    [
      'work',
      'sleep',
      'Both work and sleep can be associated with the idea of surrender or release—work as a way to let go of our personal desires and serve the needs of a company, organization, or the greater good, and sleep as a way to surrender control and trust in the natural processes of our bodies and minds.'
    ],
    [
      'baby',
      'gun',
      'Both a baby and a gun can be associated with a sense of risk and danger—a baby by its need to be handled with care to prevent injury or harm, and a gun by its ability to cause great harm in the wrong hands.'
    ]
  ]
}

export const SCENE_PROMPT_COMPONENTS = {
  preamble:
    'Sensory details are details that appeal to the five senses: vision, hearing, touch, smell, and taste. Sensory details make our writing more interesting and vivid, and the most effective sensory details are ones that are creative yet concrete and evocative. For each thing below, we provide a list of sensory details that evoke that thing.',
  prefixes: [
    `Here is a thing${PREFIX_DELIMITER}`,
    `Here are some sensory details that evoke that thing${PREFIX_DELIMITER}`
  ],
  examples: [
    [
      'NYC subway car',
      [
        'A discarded slushie cup dripping red liquid onto a seat',
        "The conductor saying something over the speaker, but the sound is too muffled to make out what they're saying",
        'A person doing acrobatic maneuvers on the grab bars',
        'Rats scurrying through the train tracks',
        'A busker giving a mediocre performance'
      ].join('\n')
    ],
    [
      'tech company office',
      [
        'A group of software engineers lounging in "nap pods"',
        'Your boss joining a meeting from a desk that is attached to a treadmill',
        'The crinkling of snack wrappers as a custodial worker replenishes the free snacks in the kitchen',
        'Kombucha and cold brew on tap',
        "Modern, angular furniture that isn't very comfortable "
      ].join('\n')
    ],
    [
      'my abuela',
      [
        'A giant pot of rice and beans simmering on the stove',
        'A tiny radio on the counter playing music from her home country',
        'A rosary hanging on the wall',
        'Her speaking to me in Spanish and me responding in English',
        'The sound of knitting needles gently clanking together'
      ].join('\n')
    ],
    [
      'standing in line at the DMV',
      [
        'An anxious teenager who is visibly dissatisfied with their new license photo but too nervous to ask to retake it',
        'A pen with a plastic spoon taped to it to prevent people from taking it',
        'A very loud air conditioning unit that is doing a poor job of cooling the place down',
        'A woman with screaming children talking on the phone',
        'A vaguely musty smell'
      ].join('\n')
    ],
    [
      'boarding a plane',
      [
        'A faint smell of jet fumes as the plane taxis toward the runway',
        'The pilot\'s voice over the speaker saying, "Attention passengers, this is your pilot speaking..."',
        'A young child repeatedly opening and closing the window shade',
        'A tiny dog stuffed in a carrier beneath the seat',
        'A flight attendant explaining the emergency evacuation procedures to the people seated in the exit row'
      ].join('\n')
    ],
    [
      'a Korean spa',
      [
        'The smell of eucalyptus and hot wood',
        'The sound of a shocked gasp when a guest realizes that they have accidentally stepped into the cool bath instead of the hot bath',
        'A heap of discarded white towels',
        'A food court that sells all of the Korean food staples',
        'Matching spa uniforms'
      ].join('\n')
    ]
  ]
}

export const UNFOLD_PROMPT_COMPONENTS = {
  preamble: '',
  prefixes: [
    `Here is a target word${PREFIX_DELIMITER}`,
    `Here are some ways the target word appears in other words and phrases${PREFIX_DELIMITER}`
  ],
  examples: [
    [
      'space',
      [
        'outer space',
        'space suit',
        'Space Age (historical period)',
        'backspace',
        'space heater',
        'parking space',
        'space-time continuum',
        'Space Invaders (video game)',
        'crawl space',
        'latent space',
        'Lost in Space (TV series)'
      ].join('\n')
    ],
    [
      'back',
      [
        'backup',
        'backpack',
        'back-to-back',
        'comeback',
        'throwback',
        "the straw that broke the camel's back",
        'back and forth',
        'callback',
        'backgammon',
        'back against the wall',
        'back burner',
        'circle back',
        'dial back',
        "have someone's back"
      ].join('\n')
    ],
    [
      'run',
      [
        'run away',
        'home run',
        "run for one's money",
        'dry run',
        'run the show',
        'on the run',
        'run a red light',
        'run in circles',
        'run for office',
        'running on fumes',
        'still waters run deep',
        'runny nose'
      ].join('\n')
    ],
    [
      'brain',
      [
        'brainstorm',
        'brain freeze',
        'brain dead',
        "pick someone's brain",
        'brain fart',
        'Pinky and The Brain (TV series)',
        'brain bucket',
        'brain tumor',
        "rack one's brain",
        'brain teaser',
        'brain cramp',
        'scatterbrained'
      ].join('\n')
    ],
    [
      'jump',
      [
        'jump-start',
        'jump the gun',
        'jump at the chance',
        'jump the shark',
        'jump ship',
        'jump rope',
        'jump on the bandwagon',
        'jumpsuit',
        "jump out of one's skin",
        'jump to conclusions',
        'jump for joy',
        'hop, skip, and a jump'
      ].join('\n')
    ],
    [
      'free',
      [
        'free will',
        'Free Willy (1993 film)',
        'scot-free',
        'free-for-all',
        'freestyle',
        'free time',
        'freeloader',
        'free agent',
        'freehand',
        'free range',
        'home free',
        'free rein',
        'if you love someone, set them free'
      ].join('\n')
    ],
    [
      'light',
      [
        'spotlight',
        'lightsaber',
        'Northern Lights (Aurora Borealis)',
        'light year',
        'light at the end of the tunnel',
        'traffic light',
        'make light of',
        'gaslight',
        'light as a feather',
        'red-light district',
        'in light of',
        'daylight',
        'lights-out'
      ].join('\n')
    ],
    [
      'i',
      [
        'I-beam',
        "dot the i's and cross the t's",
        'iPhone',
        'I-95 (interstate)',
        'I, Robot (2004 film)',
        'i.e.',
        'IHOP (restaurant)'
      ].join('\n')
    ],
    [
      'force',
      [
        'workforce',
        'tour de force',
        'force field',
        'force-feed',
        'force of habit',
        'force quit',
        "force someone's hand",
        'by force',
        'brute force',
        'force of nature',
        'a force to be reckoned with',
        'may the Force be with you (quote from Star Wars franchise)'
      ].join('\n')
    ],
    [
      'bar',
      [
        'raise the bar',
        'bar of gold',
        'bar fight',
        'bar exam',
        'bar of soap',
        'bartender',
        'handlebar',
        'barcode',
        'wine bar',
        'bar mitzvah'
      ].join('\n')
    ],
    [
      '2',
      [
        '2-for-1',
        'two peas in a pod',
        'two-ply',
        'catch-22',
        'one-two combo',
        'two-party system',
        "two wrongs don't make a right",
        'two cents',
        'lesser of two evils',
        'two-faced',
        'it takes two to tango',
        'two-sided',
        'two-step',
        'put two and two together',
        'two sides of the same coin',
        'two-timer'
      ].join('\n')
    ],
    [
      'chain',
      [
        'chain reaction',
        'chain-link fence',
        'food chain',
        'chain gang',
        'chain of events',
        'ball and chain',
        'chain mail',
        'chainsaw',
        'fast food chain',
        'email chain',
        "yank someone's chain",
        'off the chain'
      ].join('\n')
    ],
    [
      'break',
      [
        'breakthrough',
        'break a leg',
        'break even',
        'break the cycle',
        'lunch break',
        'break a sweat',
        'break a promise',
        'lucky break',
        'break the bank',
        'icebreaker',
        'break bread',
        'break in',
        'break up',
        'spring break',
        'clean break',
        "break someone's heart"
      ].join('\n')
    ],
    [
      'king',
      [
        'king bed',
        'king of the hill',
        'king-sized',
        'The Lion King (1994 film)',
        'kingpin',
        'King Kong (fictional character)',
        'fit for a king',
        'king of the jungle',
        'king of spades'
      ].join('\n')
    ],
    [
      'x',
      [
        'X marks the spot',
        'X-Men (fictional superhero team)',
        'Malcolm X (human rights activist)',
        'X-rated',
        'Generation X (demographic cohort)',
        'X-ray',
        'X-mas (Christmas)',
        'X Games (action sports event)',
        'Xbox (video game console)',
        'Solve for x'
      ].join('\n')
    ]
  ]
}
