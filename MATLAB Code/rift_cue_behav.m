%% ===============================
%  TWO-CUE FLICKER + DOT TASK
%  (RESPONSE DURING DOT ALLOWED)
%% ===============================

sca; close all; clear;
PsychDefaultSetup(2);
KbName('UnifyKeyNames');

ESCAPE = KbName('ESCAPE');
LEFT   = KbName('LeftArrow');
RIGHT  = KbName('RightArrow');

%% ===============================
% SETTINGS
%% ===============================
numTrials     = 40;

cueDuration   = 1.5;
dotDuration   = 0.2;
itiRange      = [0.6 1.0];

flickerFreq   = 60;
stimRadius    = 80;
dotRadius     = 8;
sigma         = 0.35;

greyBG        = [0.5 0.5 0.5];
black         = [0 0 0];

% Fixation
fixRadius     = 4;
fixColor      = [0 0 0];

% Flicker parameters
baseLumStatic = 0.68;
baseLumFlick  = 0.65;
flickerAmp    = 0.25;

%% ===============================
% SCREEN SETUP
%% ===============================
Screen('Preference','SkipSyncTests',1);
screens = Screen('Screens');
screenNumber = min(screens);

[win, rect] = PsychImaging('OpenWindow', screenNumber, greyBG);
Screen('BlendFunction', win, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

ifi = Screen('GetFlipInterval', win);
fps = 1/ifi;

[xCenter, yCenter] = RectCenter(rect);
fixPos = [xCenter yCenter];

Priority(MaxPriority(win));

%% ===============================
% POSITIONS
%% ===============================
offsetX = 200;

leftPos  = [xCenter - offsetX, yCenter];
rightPos = [xCenter + offsetX, yCenter];

leftRect  = CenterRectOnPointd([0 0 stimRadius*2 stimRadius*2], leftPos(1),  leftPos(2));
rightRect = CenterRectOnPointd([0 0 stimRadius*2 stimRadius*2], rightPos(1), rightPos(2));

%% ===============================
% PRECOMPUTE FLICKER
%% ===============================
numFrames = round(cueDuration / ifi);
t = (0:numFrames-1) / fps;
flickerMod = sin(2*pi*flickerFreq*t);

%% ===============================
% GAUSSIAN MASK
%% ===============================
res = stimRadius * 2;
[x, y] = meshgrid(linspace(-1,1,res), linspace(-1,1,res));
r2 = x.^2 + y.^2;

gaussMask = exp(-r2/(2*sigma^2));
gaussMask(r2 > 1) = 0;

circleRGBA = zeros(res, res, 4);
circleRGBA(:,:,1:3) = 1;
circleRGBA(:,:,4)   = gaussMask;

stimTexture = Screen('MakeTexture', win, circleRGBA);

%% ===============================
% CONDITIONS
%% ===============================
cueFlickerSide = randi(2, numTrials, 1);
dotSide        = randi(2, numTrials, 1);

results = table(cueFlickerSide, dotSide, ...
    nan(numTrials,1), nan(numTrials,1), ...
    'VariableNames', {'flickerSide','dotSide','resp','RT'});

%% ===============================
% TRIAL LOOP
%% ===============================
for tIdx = 1:numTrials

    %% -------- CUE --------
    vbl = Screen('Flip', win);

    for f = 1:numFrames

        Screen('FillRect', win, greyBG);

        leftLum  = baseLumStatic;
        rightLum = baseLumStatic;

        if cueFlickerSide(tIdx) == 1
            leftLum = baseLumFlick + flickerAmp * flickerMod(f);
        else
            rightLum = baseLumFlick + flickerAmp * flickerMod(f);
        end

        leftLum  = max(min(leftLum,1),0);
        rightLum = max(min(rightLum,1),0);

        Screen('DrawTexture', win, stimTexture, [], leftRect,  [], [], [], [leftLum leftLum leftLum]);
        Screen('DrawTexture', win, stimTexture, [], rightRect, [], [], [], [rightLum rightLum rightLum]);

        Screen('DrawDots', win, fixPos', fixRadius*2, fixColor, [], 2);

        vbl = Screen('Flip', win, vbl + 0.5*ifi);
        checkESC(ESCAPE);
    end

    %% -------- DOT + RESPONSE --------
    Screen('FillRect', win, greyBG);

    if dotSide(tIdx) == 1
        dotPos = leftPos;
    else
        dotPos = rightPos;
    end

    Screen('DrawDots', win, dotPos', dotRadius*2, black, [], 2);
    Screen('DrawDots', win, fixPos', fixRadius*2, fixColor, [], 2);

    dotOnset = Screen('Flip', win);
    respStart = dotOnset;

    responded = false;
    resp = NaN;

    % --- DOT DISPLAY WINDOW ---
    while GetSecs - dotOnset < dotDuration && ~responded
        [keyDown, ~, keyCode] = KbCheck;
        if keyDown
            if keyCode(LEFT)
                resp = 1; responded = true;
            elseif keyCode(RIGHT)
                resp = 2; responded = true;
            elseif keyCode(ESCAPE)
                sca; return;
            end
        end
    end

    % --- POST-DOT RESPONSE WINDOW ---
    Screen('FillRect', win, greyBG);
    Screen('DrawDots', win, fixPos', fixRadius*2, fixColor, [], 2);
    Screen('Flip', win);

    while ~responded
        [keyDown, ~, keyCode] = KbCheck;
        if keyDown
            if keyCode(LEFT)
                resp = 1; responded = true;
            elseif keyCode(RIGHT)
                resp = 2; responded = true;
            elseif keyCode(ESCAPE)
                sca; return;
            end
        end
    end

    results.resp(tIdx) = resp;
    results.RT(tIdx)   = GetSecs - respStart;
    
    %% -------- ITI --------
    Screen('FillRect', win, greyBG);
    Screen('DrawDots', win, fixPos', fixRadius*2, fixColor, [], 2);
    Screen('Flip', win);

    WaitSecs(itiRange(1) + rand * diff(itiRange));

end

results.cue_type = strings(height(results),1);
results.correct = zeros(height(results),1);

results.cue_type(results.flickerSide == results.dotSide)  = "valid";
results.cue_type(results.flickerSide ~= results.dotSide) = "invalid";
results.correct(results.resp == results.dotSide)  = 1;
results.correct(results.resp ~= results.dotSide) = 0;



%% ===============================
% CLEANUP
%% ===============================
Priority(0);
sca;

disp('Finished!');
disp(results);

%% ===============================
% ESC FUNCTION
%% ===============================
function checkESC(ESCAPE)
    [keyIsDown,~,keyCode] = KbCheck;
    if keyIsDown && keyCode(ESCAPE)
        sca;
        error('Experiment aborted.');
    end
end
