% stimuli are circles
% textures but filloval
% gaussian mask
% stim border


%% ===== TWO-STIMULUS CUE + FLICKER TASK (FULLCIRCLE, PRECOMPUTED TEXTURE) =====
sca; close all; clear;
PsychDefaultSetup(2);

KbName('UnifyKeyNames');
ESCAPE = KbName('ESCAPE');


%% ===== SETTINGS =====

% devices
EEGON = false; eyetrackerON = 0;

numPracTrials  = 0;
numTrials      = 4;      % trials per block
numAwareTrials = 10;
numBlocks      = 2;      % number of blocks (including practice)

fracMatch      = 0.5;    % fraction of trials where probe matches cue
% trial timing
cueDuration   = 0.75;
fixRange      = [0,0];
stimDuration  = 2;
itiRange      = [0.5,0.8];
awareDuration = stimDuration;    

% stimuli
freq_flicker  = 60;   % Hz
stimBorder    = true;
stimRadius    = 100;  % radius of stimulus (cue/probe will match)
sigma         = 0.35; % gaussian edge softness

outerRadius   = stimRadius * 0.7; 
innerRadius   = outerRadius * 0.6;

fixDotSize    = 10;
fixDotColor   = [0 0 0];

% Colors (normalized 0-1)
color1 = [1 0 0];       % red
color2 = [0 1 1];       % cyan
color3 = [0 0 1];       % blue
color4 = [1 1 0];       % yellow
colorPairs = { {color1,color2}, {color3,color4} };

%% ===== EEG SETUP (BioSemi) =====
if EEGON
    % Detect COM port 
    comport  = 'COM3';          % <-- CHANGE THIS
    baudrate = 115200;
    srl = serialport(comport, baudrate);
    
    % Make sure line starts low
    write(srl, uint8(0), 'uint8');
else
    srl = [];
end

%% ===== EEG TRIGGER CODES =====
TRIG = struct();

TRIG.CUE_ON        = 10;
TRIG.STIM_ON       = 20;
TRIG.PROBE_ON      = 30;
TRIG.RESP_SAME     = 40;
TRIG.RESP_DIFF     = 41;
TRIG.AWARE_STIM_ON = 50;
TRIG.BLOCK_START   = 90;
TRIG.BLOCK_END     = 91;


%% ===== SCREEN SETUP =====
screens = Screen('Screens');
screenNumber = min(screens);
Screen('Preference','SkipSyncTests',1);
grey  = 0.5;
[window, windowRect] = PsychImaging('OpenWindow',screenNumber,[grey grey grey]);
Screen('BlendFunction', window, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
ifi = Screen('GetFlipInterval',window);
fps = 1/ifi;
[xCenter, yCenter] = RectCenter(windowRect);
Priority(MaxPriority(window));

%% ===== PRECOMPUTE FLICKER MODULATION =====
numFrames = round(stimDuration / ifi);
tvec = (0:numFrames-1) / fps;
flickerMod = sin(2*pi*freq_flicker*tvec);  % -1 to 1

%% ===== PRECOMPUTE CONDITIONS =====
[cueColorsAll,cueOuterIdx, stimColorsAll, probeColorsAll, outputTable] = createConditions(numTrials,numBlocks,colorPairs,fracMatch);

%% ===== PRECOMPUTE GAUSSIAN ALPHA MASK =====
res = stimRadius*2;
[x, y] = meshgrid(linspace(-1,1,res), linspace(-1,1,res));
r2 = x.^2 + y.^2;
gaussMask = exp(-r2/(2*sigma^2));
gaussMask(r2>1) = 0;  % hard cutoff outside circle
circleRGBA = zeros(res,res,4);
circleRGBA(:,:,1:3) = 1;        % base white
circleRGBA(:,:,4) = gaussMask;
stimTexture = Screen('MakeTexture', window, circleRGBA);

%% ===== PRECOMPUTE FRAME COLORS FOR ALL TRIALS =====
frameColorsAll = cell(numBlocks,numTrials);
for b = 1:numBlocks
    for t = 1:numTrials
        c1 = stimColorsAll{b,t}{1};
        c2 = stimColorsAll{b,t}{2};
        baseColor = (c1+c2)/2;
        diffColor = (c2-c1)/2;
        colors = zeros(numFrames,3);
        for f = 1:numFrames
            colors(f,:) = baseColor + diffColor * flickerMod(f);
            colors(f,:) = min(max(colors(f,:),0),1);
        end
        frameColorsAll{b,t} = colors;
    end
end

%% ===== DROPPED FRAME INFO =====
droppedCount   = zeros(numBlocks,numTrials);
droppedFrames  = cell(numBlocks,numTrials);
missedTimes    = cell(numBlocks,numTrials);


%% ===== TASK INSTRUCTIONS (improved) =====
% Clear screen and show improved, split instructions with an example.
% Requires: Psychtoolbox window handle 'window', xCenter,yCenter, stimRadius, innerRadius, grey.

% -- Safety defaults (only set if not already defined) --
if ~exist('window','var') || isempty(window)
    PsychImaging('OpenWindow', max(Screen('Screens')), 0.5);
    wins = Screen('Windows');
    window = wins(end);
end
if ~exist('grey','var') || isempty(grey)
    grey = 0.5;
end
if ~exist('xCenter','var') || ~exist('yCenter','var') || isempty(xCenter) || isempty(yCenter)
    [xCenter, yCenter] = RectCenter(Screen('Rect', window));
end
if ~exist('stimRadius','var') || isempty(stimRadius)
    stimRadius = 80;
end
if ~exist('innerRadius','var') || isempty(innerRadius)
    innerRadius = round(stimRadius * 0.6);
end

% -- Instruction text (split, clearer, corrected typos) --
Screen('FillRect', window, grey);
instrStr = [ ...
    'Welcome!\n\n' ...
    'Task overview (short):\n\n\n' ...
    '  1) You will briefly see a circle composed of two colours (the memory item).\n\n\n' ...
    '  2) Then a black circle will appear for a short delay. Do NOT respond during the black circle — keep the colours in memory.\n\n\n' ...
    '  3) After the delay a probe circle (two colours) will appear.\n\n\n' ...
    '  4) Decide whether the probe colours are the SAME as the memory item or DIFFERENT.\n\n\n' ...
    'Response keys:\n\n\n' ...
    '     Press 1 = SAME\n' ...
    '     Press 2 = DIFFERENT\n\n\n' ...
    'If unsure, please guess.\n\n\n' ...
    '--- Press any key to see an example ---' ...
];
DrawFormattedText(window, instrStr, 'center', 'center', [0 0 0], 70);
Screen('Flip', window);
KbReleaseWait;

while true
    checkESC(ESCAPE);
    [keyIsDown, ~, ~] = KbCheck;
    if keyIsDown
        break;
    end
    WaitSecs(0.01);
end

%% ===== WORKED EXAMPLE =====
% Display a short, annotated example sequence:
%  1) Memory item (two-colour circle) for cueDuration
%  2) Black circle (delay) for a short duration
%  3) Probe (two-colour circle) and show how to respond

% Example timing (adjust to match your experiment parameters)
cueDurationEx   = 2;   % seconds for memory item in example
delayDurationEx = 2;   % black circle duration in example
probeHoldEx     = 2;   % time probe is shown while waiting for example response

% Example colours (RGB 0..1)
exTopOuter = [0.9 0.4 0.2];   % outer colour memory item
exTopInner = [0.2 0.6 0.9];   % inner colour memory item
% Example probe: show a MATCH case here (change to demonstrate DIFFERENT if desired)
exProbeOuter = exTopOuter;
exProbeInner = exTopInner;

% Positions
offsetY = 0;  % keep centered for example
outerRectEx = CenterRectOnPointd([0 0 stimRadius*2 stimRadius*2], xCenter, yCenter + offsetY);
innerRectEx = CenterRectOnPointd([0 0 innerRadius*2 innerRadius*2], xCenter, yCenter + offsetY);

% --- 1) Memory item ---
Screen('FillRect', window, grey);
Screen('FillOval', window, exTopOuter, outerRectEx);
Screen('FillOval', window, exTopInner, innerRectEx);  
DrawFormattedText(window, 'Memory item: remember these two colours', 'center', yCenter + stimRadius + 40, [0 0 0], 70);
DrawFormattedText(window, '--- Press any key to continue ---', 'center', yCenter + stimRadius + 100, [0 0 0], 70);

Screen('Flip', window);
KbReleaseWait;

while true
    checkESC(ESCAPE);
    [keyIsDown, ~, ~] = KbCheck;
    if keyIsDown
        break;
    end
    WaitSecs(0.01);
end

% --- 2) Delay (black circle) ---
Screen('FillRect', window, grey);
stimRect = CenterRectOnPointd([0 0 stimRadius*2 stimRadius*2], xCenter, yCenter);
borderWidth = 8;
shrinkOuter = 10;  
frameRect = InsetRect(stimRect, shrinkOuter + borderWidth/2, shrinkOuter + borderWidth/2);
Screen('FrameOval', window, [0 0 0], frameRect, borderWidth);
DrawFormattedText(window, 'Delay: keep the colours in memory (do not respond yet)', 'center', yCenter + stimRadius + 40, [0 0 0], 70);
DrawFormattedText(window, '--- Press any key to continue ---', 'center', yCenter + stimRadius + 100, [0 0 0], 70);

Screen('Flip', window);
KbReleaseWait;

while true
    checkESC(ESCAPE);
    [keyIsDown, ~, ~] = KbCheck;
    if keyIsDown
        break;
    end
    WaitSecs(0.01);
end

% --- 3) Probe and instruct response ---
Screen('FillRect', window, grey);
Screen('FillOval', window, exProbeOuter, outerRectEx);
Screen('FillOval', window, exProbeInner, innerRectEx);
DrawFormattedText(window, 'Probe: are these the SAME or DIFFERENT?', 'center', yCenter - stimRadius - 60, [0 0 0], 70);
DrawFormattedText(window, 'Press 1 = SAME    Press 2 = DIFFERENT', 'center', yCenter + stimRadius + 40, [0 0 0], 70);
DrawFormattedText(window, '--- Press any key to continue ---', 'center', yCenter + stimRadius + 100, [0 0 0], 70);
Screen('Flip', window);

KbReleaseWait;
% Wait for any key to continue (allow escape to abort)
while true
    checkESC(ESCAPE);
    [keyIsDown, ~, ~] = KbCheck;
    if keyIsDown
        break;
    end
    WaitSecs(0.01);
end
FlushEvents('keyDown'); % clear keyboard queue

%% ===== CONFIRMATION SCREEN =====
Screen('FillRect', window, grey);
finalMsg = sprintf([ ...
    'The experiment consists of N blocks.\n\n' ...
    'Between blocks you can take a small break.\n\n\n' ...
    'If anything is unclear, please ask the experimenter to explain now.\n\n' ...
    'If everything is clear you can press any key to start the experiment.\n\n' ...
]);

DrawFormattedText(window, finalMsg, 'center', 'center', [0 0 0], 70);
Screen('Flip', window);

KbReleaseWait;
% Wait for any key (or ESC to quit)
while true
    [keyIsDown, ~, keyCode] = KbCheck;
    if keyIsDown  
        if keyCode(KbName('ESCAPE'))
            sca;
            return;
        else
            break;
        end
    end
    WaitSecs(0.01);
end

% short pause then continue to block/trials
Screen('FillRect', window, grey);
Screen('Flip', window);
WaitSecs(0.2);

% End of instruction + example section. Continue with your trial loop.

%% ===== create table for output =====

outputTable.resp = nan(height(outputTable),1);
outputTable.correct = false(height(outputTable),1);  % initialize all to false
outputTable.RT = nan(height(outputTable),1);            % initialize all to NaN
missed_fr = 0;
missed_traces{1,1} = [];

%% ===== TRIAL LOOP =====
% try
for b = 1:numBlocks
    if EEGON
        sendTrigger(srl, TRIG.BLOCK_START);
    end

    if b == 1 
        % Practice block
        nTrials = numPracTrials;
        blockName = 'Practice';
    else
        % Real experiment blocks
        nTrials = numTrials;
        blockName = sprintf('Block %d', b-1);
    end

    % real experiment
    for trial = 1:nTrials
            globalTrial = (b-1)*nTrials + trial;

            cueColors   = cueColorsAll{b,trial};
            colorsFrames= frameColorsAll{b,trial};
            probeColors = probeColorsAll{b,trial};
            probeType   = outputTable.probeType{ (b-1)*numTrials + trial }; % 'match' or 'change'

            %% ===== CUE =====
            outerRect = CenterRectOnPointd([0 0 outerRadius*2 outerRadius*2], xCenter, yCenter);
            innerRect = CenterRectOnPointd([0 0 innerRadius*2 innerRadius*2], xCenter, yCenter);
            Screen('FillOval', window, cueColors{cueOuterIdx}, outerRect);
            Screen('FillOval', window, cueColors{3-cueOuterIdx  }, innerRect);
            Screen('Flip', window);
            if EEGON
                sendTrigger(srl, TRIG.CUE_ON);
            end
            WaitSecs(cueDuration);

            %% ===== FIXATION delay =====
            Screen('FillRect', window, grey);
            Screen('DrawDots', window, [xCenter; yCenter], fixDotSize, fixDotColor, [], 2);
            Screen('Flip', window);
            fixDuration = fixRange(1) + (fixRange(2)-fixRange(1))*rand;
            WaitSecs(fixDuration);

            %% ===== STIMULUS =====
            vbl = Screen('Flip', window);
            if EEGON
                sendTrigger(srl, TRIG.STIM_ON);
            end
            stimRect = CenterRectOnPointd([0 0 stimRadius*2 stimRadius*2], xCenter, yCenter);

            % draw static black border
            if stimBorder
                borderWidth = 8;
                shrinkOuter = 10;  
                frameRect = InsetRect(stimRect, shrinkOuter + borderWidth/2, shrinkOuter + borderWidth/2);
            end

            for f = 1:numFrames
                Screen('DrawTexture', window, stimTexture, [], stimRect, [], [], [], colorsFrames(f,:));
                if stimBorder
                    Screen('FrameOval', window, [0 0 0], frameRect, borderWidth);
                end
                [vbl, ~, ~, missed] = Screen('Flip', window, vbl + 0.5*ifi);
                if missed>0
                    droppedCount(b,trial) = droppedCount(b,trial)+1;
                    droppedFrames{b,trial}(end+1) = f;
                    missedTimes{b,trial}(end+1) = missed;
                end
            end

            %% ===== PROBE =====
            Screen('FillOval', window, probeColors{2}, outerRect);
            Screen('FillOval', window, probeColors{1}, innerRect);
            Screen('Flip', window);
            if EEGON
                sendTrigger(srl, TRIG.PROBE_ON);
            end
            respKey = NaN;
            respStart = GetSecs;
            timeoutSec = 2;

            KbReleaseWait;   % flush old keypresses

            while GetSecs - respStart < timeoutSec
                [keyIsDown, ~, keyCode] = KbCheck;
                if keyIsDown
                    if keyCode(KbName('1!'))
                        respKey = 1;
                        break;
                    elseif keyCode(KbName('2@'))
                        respKey = 2;
                        break;
                    end
                end
            end

            RT = GetSecs - respStart;

            if EEGON;
                if respKey == 1; sendTrigger(srl,TRIG.RESP_SAME); end
            else
                if respKey == 2; sendTrigger(srl,TRIG.RESP_DIFF); end
            end
            correctResp = (respKey==1 && strcmp(probeType,'match')) || (respKey==2 && strcmp(probeType,'change'));

            outputTable.resp(globalTrial)    = respKey;
            outputTable.correct(globalTrial) = correctResp;
            outputTable.RT(globalTrial)      = RT;

            % if incorrect, give warning message
            if ~correctResp
                Screen('FillRect', window, grey);
                instrStr = 'Wrong!\n';
                DrawFormattedText(window, instrStr, 'center', 'center', [0 0 0]);
                Screen('Flip', window);
                WaitSecs(0.3);

            end


            %% ===== INTERTRIAL =====
            Screen('FillRect', window, grey);
            Screen('DrawDots', window, [xCenter; yCenter], fixDotSize, fixDotColor, [], 2);
            Screen('Flip', window);
            itiDuration = itiRange(1) + (itiRange(2)-itiRange(1))*rand;
            WaitSecs(itiDuration);
    end

    %% ===== END OF BLOCK FEEDBACK =====
    Screen('FillRect', window, grey);

    if b == 1
        % Practice block
        blockTrials = 1:numPracTrials;
    else
        blockTrials = ( (b-2)*nTrials + 1 ) : ((b-1)*nTrials);
    end
    accBlock = mean(outputTable.correct(blockTrials))*100;
    RTblock  = mean(outputTable.RT(blockTrials))*1000;

    if b == 1
        instrStr = sprintf(['End of Practice\n\n\n' ...
            'Your accuracy was: %.1f%%\n\n' ...
            'Your average reaction time was: %.0f ms\n\n\n' ...
            'Well done! Now you will continue with the real experiment.\n\n' ...
            'Press any key when you want to continue.'], accBlock, RTblock);
    else

        instrStr = sprintf(['%s\n\n\n' ...
            'Your accuracy this block was: %.1f%%\n\n' ...
            'Your average reaction time was: %.0f ms\n\n\n' ...
            'You can take a small break.\n\n' ...
            'Press any key when you want to continue.'], blockName, accBlock, RTblock);
    end

    % Display the message
    DrawFormattedText(window, instrStr, 'center', 'center', [0 0 0]);
    Screen('Flip', window);

    % Wait for a key press
    KbStrokeWait;



end


%% ===== AWARENESS TEST =======


% -------------------------
% Instruction screen
% -------------------------
Screen('FillRect', window, grey);
instrStr = sprintf([ ...
    'Well done — you have completed all blocks!\n\n' ...
    'You are almost finished, you will have to perform one last task.\n\n\n' ...
    '--- Press any key to continue ---' 
]);

DrawFormattedText(window, instrStr, 'center', 'center', [0 0 0], 70);
Screen('Flip', window);
KbReleaseWait;
while true
    checkESC(ESCAPE);
    [keyIsDown, ~, ~] = KbCheck;
    if keyIsDown
        break;
    end
    WaitSecs(0.01);
end

Screen('FillRect', window, grey);
instrStr = sprintf([ ...
    'Final task (short):\n\n\n' ...
    'You will now see three circles on each trial:\n\n\n' ...
    '  • A target circle at the top showing two colours.\n\n\n' ...
    '  • Two choice circles below: one on the LEFT and one on the RIGHT.\n\n\n' ...
    '  • The circles to the left and right have a black outline.\n\n\n' ...
    '--- Press any key to continue ---'

    ]);

DrawFormattedText(window, instrStr, 'center', 'center', [0 0 0], 70);
Screen('Flip', window);
KbReleaseWait;

while true
    checkESC(ESCAPE);
    [keyIsDown, ~, ~] = KbCheck;
    if keyIsDown
        break;
    end
    WaitSecs(0.01);
end

instrStr = sprintf([ ...
    'Your job:\n\n\n' ...
    '  • Decide whether the interior colour of the LEFT or RIGHT circle matches the target circle at the top.\n\n\n' ...
    '  • Press the LEFT key if you think the LEFT circle matches the top.\n\n\n' ...
    '  • Press the RIGHT key if you think the RIGHT circle matches the top.\n\n\n' ...
    'If you are unsure, make your best guess.\n\n\n' ...
    '--- Press any key to see an example ---' ...
]);

DrawFormattedText(window, instrStr, 'center', 'center', [0 0 0], 70);
Screen('Flip', window);
KbReleaseWait;

while true
    checkESC(ESCAPE);
    [keyIsDown, ~, ~] = KbCheck;
    if keyIsDown
        break;
    end
    WaitSecs(0.01);
end

% -------------------------
% Example display (static; no flicker)
% -------------------------
% Example colours (RGB in range 0..1). Replace these with your trial values as needed.
topOuter = [0.8 0.2 0.2];    % example outer colour
topInner = [0.2 0.6 0.9];    % example inner colour (the "match")
leftFill  = [0.5 0.5 0.5     ];        % left matches the top inner colour
rightFill = [0.5 0.5 0.5];   % non-matching example

offsetX = 200;
offsetY = 150;
borderWidth = 6;

topPos   = [xCenter, yCenter - offsetY];
leftPos  = [xCenter - offsetX, yCenter + offsetY];
rightPos = [xCenter + offsetX, yCenter + offsetY];

outerRectTop  = CenterRectOnPointd([0 0 stimRadius*2 stimRadius*2], topPos(1), topPos(2));
innerRectTop  = CenterRectOnPointd([0 0 innerRadius*2 innerRadius*2], topPos(1), topPos(2));

rectLeft  = CenterRectOnPointd([0 0 stimRadius*2 stimRadius*2], leftPos(1), leftPos(2));
rectRight = CenterRectOnPointd([0 0 stimRadius*2 stimRadius*2], rightPos(1), rightPos(2));

% Draw example
Screen('FillRect', window, grey);

% Top target: outer + inner to show two colours
Screen('FillOval', window, topOuter, outerRectTop);
Screen('FillOval', window, topInner, innerRectTop);

% Left and right choice circles
Screen('FillOval', window, leftFill, rectLeft);
Screen('FillOval', window, rightFill, rectRight);

% Black outlines for choice circles
Screen('FrameOval', window, [0 0 0], rectLeft,  borderWidth);
Screen('FrameOval', window, [0 0 0], rectRight, borderWidth);

% Labels under choices
DrawFormattedText(window, 'LEFT KEY',  leftPos(1)-65, leftPos(2)+stimRadius+30, [0 0 0], 100);
DrawFormattedText(window, 'RIGHT KEY', rightPos(1)-65, rightPos(2)+stimRadius+30, [0 0 0], 100);

% Add "press any key to continue" message at bottom
contMsg = '--- Press any key to continue continue ---';
DrawFormattedText(window, contMsg, 'center', yCenter + offsetY + stimRadius + 80, [0 0 0], 70);

Screen('Flip', window);
KbStrokeWait;

% -------------------------
% Final "start block" screen
% -------------------------
Screen('FillRect', window, grey);
finalMsg = sprintf([ ...
    'If anything is unclear, please ask the experimenter to explain.\n\n' ...
    'If all is clear you can press any key to start the final task.\n\n' ...
]);

DrawFormattedText(window, finalMsg, 'center', 'center', [0 0 0], 70);
Screen('Flip', window);
KbStrokeWait;

% Small pause and continue
Screen('FillRect', window, grey);
Screen('Flip', window);
WaitSecs(0.2);
     


%% ===== CONDITIONS =====

% create conditions
awareConditions = createAwarenessConditions(numAwareTrials, colorPairs);

% initialize response columns
awareConditions.resp = nan(height(awareConditions),1);
awareConditions.correct = false(height(awareConditions),1);  
awareConditions.RT = nan(height(awareConditions),1);   
awareConditions.timedOut = false(height(awareConditions),1) 

%% ===== PRECOMPUTE FRAME COLORS FOR ALL TRIALS =====

frameColorsAware.left  = cell(1, numAwareTrials);
frameColorsAware.right = cell(1, numAwareTrials);

for t = 1:numAwareTrials   % iterate only the aware trials (not numTrials if different)

    % left
    c1_left = awareConditions.stimLcolors{t}{1};
    c2_left = awareConditions.stimLcolors{t}{2};
    baseColor_left = (c1_left + c2_left) / 2;
    diffColor_left = (c2_left - c1_left) / 2;
    colors_left = zeros(numFrames, 3);
    for f = 1:numFrames
        colors_left(f, :) = baseColor_left + diffColor_left * flickerMod(f);
        colors_left(f, :) = min(max(colors_left(f, :), 0), 1);
    end
    frameColorsAware.left{t} = colors_left;  

    % right
    c1_right = awareConditions.stimRcolors{t}{1};
    c2_right = awareConditions.stimRcolors{t}{2};
    baseColor_right = (c1_right + c2_right) / 2;
    diffColor_right = (c2_right - c1_right) / 2;
    colors_right = zeros(numFrames, 3);
    for f = 1:numFrames
        colors_right(f, :) = baseColor_right + diffColor_right * flickerMod(f);
        colors_right(f, :) = min(max(colors_right(f, :), 0), 1);
    end
    frameColorsAware.right{t} = colors_right; 
end


%% ===== STIMULUS PRESENTATION =====

timeoutSec = 2;   % 2 second timeout, move to top


for trial = 1:numAwareTrials

    timedout = false;
    colorsL = frameColorsAware.left{trial};
    colorsR = frameColorsAware.right{trial};

    %% ===== POSITIONS =====
    offsetX = 200;
    offsetY = 150;

    topPos    = [xCenter, yCenter - offsetY];
    bottomL   = [xCenter - offsetX, yCenter + offsetY];
    bottomR   = [xCenter + offsetX, yCenter + offsetY];

    topRect     = CenterRectOnPointd([0 0 stimRadius*2 stimRadius*2], topPos(1), topPos(2));
    bottomLRect = CenterRectOnPointd([0 0 stimRadius*2 stimRadius*2], bottomL(1), bottomL(2));
    bottomRRect = CenterRectOnPointd([0 0 stimRadius*2 stimRadius*2], bottomR(1), bottomR(2));

    %% ===== BORDERS =====
    if stimBorder
        borderWidth = 8;
        shrinkOuter = 10;

        frameRectBL  = InsetRect(bottomLRect, shrinkOuter + borderWidth/2, shrinkOuter + borderWidth/2);
        frameRectBR  = InsetRect(bottomRRect, shrinkOuter + borderWidth/2, shrinkOuter + borderWidth/2);
    end

    %% ===== FIXATION delay =====
    Screen('FillRect', window, grey);
    Screen('DrawDots', window, [xCenter; yCenter], fixDotSize, fixDotColor, [], 2);
    Screen('Flip', window);
    fixDuration = fixRange(1) + (fixRange(2)-fixRange(1))*rand;
    WaitSecs(fixDuration);

    %% ===== START TIMING =====
    vbl = Screen('Flip', window);
    if EEGON
        sendTrigger(srl, TRIG.AWARE_STIM_ON);
    end
    %% ===== FRAME LOOP =====
    for f = 1:numFrames

        Screen('FillRect', window, grey);
       
        % fixation dot
        Screen('DrawDots', window, [xCenter; yCenter], fixDotSize, fixDotColor, [], 2);

        % --- Target (static ---
        outerRect = CenterRectOnPointd([0 0 outerRadius*2 outerRadius*2], topPos(1), topPos(2));
        innerRect = CenterRectOnPointd([0 0 innerRadius*2 innerRadius*2], topPos(1), topPos(2));

        Screen('FillOval', window, awareConditions.targetColorOuter{trial}, outerRect);
        Screen('FillOval', window, awareConditions.targetColorInner{trial}, innerRect);

        % --- left stimulus (flicker) ---
        Screen('DrawTexture', window, stimTexture, [], bottomLRect, ...
            [], [], [], colorsL(f,:));

        % --- right stimulus (flicker ---
        Screen('DrawTexture', window, stimTexture, [], bottomRRect, ...
            [], [], [], colorsR(f,:));

        % --- BORDERS ---
        if stimBorder
            Screen('FrameOval', window, [0 0 0], frameRectBL,  borderWidth);
            Screen('FrameOval', window, [0 0 0], frameRectBR,  borderWidth);
        end

        %% --- FLIP ---
        [vbl, ~, ~, missed] = Screen('Flip', window, vbl + 0.5*ifi);

        VBL_time = vbl;

         % Code kabir: Check for missed frames
        if nnz(diff(VBL_time) - 0.0083 > 0.004) == 0 
            VBL_time = []; % no frame missed
        else
            missed_fr = missed_fr + 1; % store missed frame
            missed_traces{globalTrial} = VBL_time;
            VBL_time = [];
        end            



    end


    %% ===== FIXATION delay =====
    Screen('FillRect', window, grey);
    Screen('DrawDots', window, [xCenter; yCenter], fixDotSize, fixDotColor, [], 2);
    Screen('Flip', window);
    KbReleaseWait;
    
    while true
        checkESC(ESCAPE);
        [keyIsDown, ~, ~] = KbCheck;
        if keyIsDown
            break;
        end
        WaitSecs(0.01);
    end

    fixDuration = fixRange(1) + (fixRange(2)-fixRange(1))*rand;
    WaitSecs(fixDuration);


    %% ===== COLLECT RESPONSE =====
    respToBeMade = true;
    respKey = NaN;
    respStart = GetSecs;
    timeoutSec = 2;   % seconds
    timedOut = false;
    
    leftCode  = KbName('LeftArrow');
    rightCode = KbName('RightArrow');
    
    while respToBeMade
        [keyIsDown, ~, keyCode] = KbCheck;
        if keyIsDown
            if keyCode(leftCode)
                respKey = 1;
                respToBeMade = false;
            elseif keyCode(rightCode)
                respKey = 2;
                respToBeMade = false;
            end
            while KbCheck; end % flush other keys
        end
    
        if GetSecs - respStart >= timeoutSec
            respToBeMade = false;
            timedOut = true;
            break;  % exit immediately
        end
    
        WaitSecs(0.001);
    end
    
    % show timeout feedback AFTER exiting loop
    if timedOut
        Screen('FillRect', window, grey);
        DrawFormattedText(window, 'Too slow!', 'center', 'center', [0 0 0]);
        Screen('Flip', window);
        WaitSecs(0.5);  % half-second feedback
    end

    RT = GetSecs - respStart;   % RT is time until response or until timeout

    % Determine correctness (handle cell-of-char correctAnswer)
    respKey = respKey(:);
    ansStr = awareConditions.correctAnswer{trial};   % change indexing if needed
    if isnan(respKey)
        correctResp = NaN;   % <-- key change
    else
        correctResp = (respKey == 1 && strcmp(ansStr,'left')) || ...
                      (respKey == 2 && strcmp(ansStr,'right'));
    end

    
    awareConditions.resp(trial)     = respKey;
    awareConditions.correct(trial)  = correctResp;
    awareConditions.RT(trial)       = RT;
    awareConditions.timedOut(trial) = timedOut;


end

respondedTrials = ~awareConditions.timedOut;

accAware = mean(awareConditions.correct(respondedTrials)) * 100;
respRate = mean(respondedTrials) * 100;

RTaware = mean(awareConditions.RT(respondedTrials), 'omitnan') * 1000;

instrStr = sprintf([ ...
    'Awareness task complete\n\n' ...
    'Accuracy (responded trials): %.1f%%\n\n' ...
    'Response rate: %.1f%%\n\n' ...
    'Mean RT: %.0f ms\n\n\n' ...
    'Press any key to continue.'], ...
    accAware, respRate, RTaware);

DrawFormattedText(window, instrStr, 'center', 'center', [0 0 0]);
Screen('Flip', window);
KbStrokeWait;


if EEGON
    write(srl, uint8(0), 'uint8');
    clear srl
end

Priority(0);
sca;

fprintf('\n=== DROPPED FRAMES ===\n');
fprintf('Frame duration: %.3f ms\n', 1000/fps);
for b=1:numBlocks
    for t=1:numTrials
        fprintf('Block %d, Trial %d: %d late frames\n', b, t, droppedCount(b,t));
    end
end

% catch err
%     Priority(0);
%     sca;
%     rethrow(err);
% end

function safeQuit()
    sca;                        % Screen('CloseAll')
    ListenChar(0);              % re-enable keyboard
    ShowCursor;
    Priority(0);
    error('Experiment aborted by user (ESC).');
end


function checkESC(ESCAPE)
    [keyIsDown, ~, keyCode] = KbCheck;
    if keyIsDown && keyCode(ESCAPE)
        safeQuit();
    end
end

