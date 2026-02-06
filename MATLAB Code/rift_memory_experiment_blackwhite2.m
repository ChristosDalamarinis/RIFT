%% ===== TWO-STIMULUS CUE + FLICKER TASK (BLACK-WHITE SQUARE) =====
sca; close all; clear;
PsychDefaultSetup(2);

%% ===== SETTINGS =====
numTrials     = 2;
cueDuration   = 0.75;
fixDuration   = 0;
stimDuration  = 1.5;
itiDuration   = 1;
freq_flicker  = 60;  % Hz

stimType = 'square';

% Stimulus size
stimSize  = 250;
res       = 200;

% Fixation
fixDotSize  = 10;
fixDotColor = [0 0 0];

%% ===== SCREEN SETUP =====
screens = Screen('Screens');
screenNumber = max(screens);

white = WhiteIndex(screenNumber);   % usually 255
black = BlackIndex(screenNumber);   % usually 0
grey  = (white + black)/2;          % mid-grey background
bg_grey = 0.6; 
[window, windowRect] = PsychImaging('OpenWindow',screenNumber,[bg_grey bg_grey bg_grey]);
ifi = Screen('GetFlipInterval',window);
[xCenter,yCenter] = RectCenter(windowRect);

Priority(MaxPriority(window));

%% ===== CREATE HARD SQUARE MASK =====
[xx,yy] = meshgrid(linspace(-1,1,res));
squareMask = (abs(xx)<=1) & (abs(yy)<=1);
squareMask = double(squareMask);   % 1 inside square, 0 outside

%% ===== PRECOMPUTE FLICKER =====
numFrames = round(stimDuration / ifi);
tvec = (0:numFrames-1)*ifi;

% Binary flicker: -1 = black, +1 = white
invertContrast = sign(sin(2*pi*freq_flicker*tvec));

%% ===== PRECOMPUTE TEXTURES =====
stimTextures = cell(numTrials,1);
dstRect = CenterRectOnPointd([0 0 stimSize stimSize],xCenter,yCenter);

for t = 1:numTrials
    stimTextures{t} = zeros(1,numFrames);

    for f = 1:numFrames
        contrastMod = invertContrast(f);

        % --- Black ↔ White flicker, square shape ---
        stimMatrix = squareMask * contrastMod;

        % Map -1 → black, +1 → white
        bwImage = (stimMatrix + 1)/2 * (white - black) + black;

        % 3-channel image
        finalImage = repmat(bwImage,[1 1 3]);

        stimTextures{t}(f) = Screen('MakeTexture', window, finalImage);
    end
end

%% ===== TRIAL LOOP =====
try
for trial = 1:numTrials

    % ---- FIXATION BASELINE ----
    Screen('FillRect', window, bg_grey);
    Screen('DrawDots', window,[xCenter;yCenter],fixDotSize,fixDotColor,[],2);
    Screen('Flip', window);
    WaitSecs(fixDuration);

    % ---- FLICKERING SQUARE ----
    vbl = Screen('Flip', window);
    for frame = 1:numFrames
        Screen('DrawTexture',window,stimTextures{trial}(frame),[],dstRect);
        vbl = Screen('Flip',window,vbl + 0.5*ifi);
    end

    % ---- INTER-TRIAL INTERVAL ----
    Screen('FillRect',window,bg_grey);
    Screen('DrawDots',window,[xCenter;yCenter],fixDotSize,fixDotColor,[],2);
    Screen('Flip',window);
    WaitSecs(itiDuration);

end

Priority(0);
sca;

catch err
Priority(0);
sca;
rethrow(err);
end
