# Apna AI Coach (FitVision)

Apna AI Coach is a webcam-based fitness application that uses pose estimation to count repetitions, track sets, check exercise form, and provide spoken coaching cues. It runs in the browser with no wearable devices or additional hardware beyond a webcam.

Built with **Streamlit**, **MediaPipe Pose**, **OpenCV**, **WebRTC**, and the **Groq** API.

## Features

- Live pose tracking with 33 body landmarks
- Automatic repetition and set counting
- Real-time form checks for each supported exercise
- Optional AI coaching text and text-to-speech feedback
- Per-user workout history stored locally
- A large, readable scoreboard that works across desktop and mobile layouts

### Supported exercises

| Exercise | Joint tracked | Form checks |
| --- | --- | --- |
| Squats | Hip-knee-ankle | Depth and forward lean |
| Push-ups | Shoulder-elbow-wrist | Body alignment and hip position |
| Biceps curls | Shoulder-elbow-wrist | Elbow drift and torso swing |
| Shoulder press | Shoulder-elbow-wrist | Arm extension and lower-back arch |
| Lunges | Front hip-knee-ankle | Knee angle and balance |

## How it works

```text
Webcam
  -> WebRTC
  -> VideoProcessor background thread
  -> MediaPipe pose landmarks
  -> Exercise-specific detector
  -> Repetition, set, and form metrics
  -> Streamlit scoreboard
  -> Optional Groq coaching and text-to-speech
  -> SQLite workout history
```

The pose detector calculates a joint angle from three landmarks \(A-B-C\):

```text
theta = arccos((BA dot BC) / (|BA| * |BC|))
```

Each exercise uses angle thresholds and a state machine to move between stages. A repetition is recorded only after a complete movement cycle, reducing false counts from jitter or partial repetitions.

## Tech stack

| Purpose | Technology |
| --- | --- |
| Web application | Streamlit |
| Live camera streaming | streamlit-webrtc |
| Pose estimation | MediaPipe Pose Landmarker |
| Image processing | OpenCV and pandas |
| AI coaching | Groq API |
| Text-to-speech | gTTS |
| Workout storage | SQLite |
| Tests | pytest |

## Getting started

### Prerequisites

- Python 3.11 or newer
- A webcam
- A modern browser
- A Groq API key, optional for AI coaching

### Installation

```bash
git clone https://github.com/A-man-Sharma-04/MINI-PROJECT.git
cd MINI-PROJECT

python -m venv .venv

# Windows
.venv\Scripts\Activate.ps1

# macOS or Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### Run

```bash
streamlit run main.py
```

Use the local URL printed by Streamlit. Browser camera access requires a secure context; use the local Streamlit URL or an HTTPS deployment.

### Using the app

1. Enter a name. An existing name loads its workout history; a new name starts a fresh history.
2. Open the **Workout** tab.
3. Choose an exercise and set the number of sets and repetitions per set.
4. Start the workout and allow browser camera access.
5. Stand 2-3 metres from the camera with your full body visible.
6. Press **End workout** when finished. Completed sets appear in the **History** tab.

For the best tracking results, use even lighting, a clear background, and a side-on view for exercises such as push-ups and lunges.

## Configuration

Settings can be provided through environment variables or `.streamlit/secrets.toml`. The app checks environment variables first.

| Setting | Purpose |
| --- | --- |
| `GROQ_API_KEY` | Enables AI coaching |
| `TURN_URLS` or `TURN_URL` | Comma-separated TURN server URLs |
| `TURN_USERNAME` | TURN username |
| `TURN_PASSWORD` | TURN password |

Example `.streamlit/secrets.toml`:

```toml
GROQ_API_KEY = "your_groq_api_key"
```

The `.streamlit/secrets.toml` file is ignored by Git. If no Groq key is configured, the application remains usable and uses built-in coaching fallback text.

For deployments behind strict NAT or firewall rules, configure TURN credentials. Google STUN and public TURN endpoints are used only when no custom TURN configuration is provided.

## Project structure

```text
main.py                         Streamlit application entry point
core/
  base_exercise.py              Shared exercise and angle logic
detectors/
  biceps_curl.py                Biceps curl detector
  lunges.py                     Lunge detector
  pushup.py                     Push-up detector
  shoulder_press.py             Shoulder press detector
  squat.py                      Squat detector
services/
  auth/                         Name-based sign-in
  coaching/                     Groq coaching and text-to-speech
  config/                       Exercise configuration
  persistence/                  SQLite repository
  state/                        Session defaults
  tracking/                     Metrics and set synchronization
  ui/                           Scoreboard and interface helpers
  vision/                       WebRTC and MediaPipe processing
ml_models/
  pose_landmarker_full.task     MediaPipe pose model
static/
  style.css                     Application styling
tests/
  test_exercise_repository.py   SQLite history tests
  test_llm_fallback.py          Coaching fallback test
```

## Adding an exercise

1. Create a detector in `detectors/` that inherits `BaseExercise`.
2. Implement the exercise's repetition and form logic.
3. Register the detector in `services/vision/exercise_video_processor.py`.
4. Add the exercise name and metrics fields to `services/config/workout_config.py`.
5. Add its label, colour, and scoreboard fields to `services/ui/scoreboard.py`.

## Database

The application creates a `data.db` SQLite database automatically. It stores usernames and workout entries:

```sql
users
  id
  username
  created_at

exercises
  id
  user_id
  exercise_name
  reps
  sets
  time
  created_at
```

Completed sets are saved immediately. Repeat entries for the same exercise and user on the same day are merged into one history row.

The name-based sign-in flow is not secure authentication and should not be treated as a user-account system.

## Tests

```bash
python -m pytest
```

The test suite covers same-day workout-history merging and AI coaching fallback behavior.

## Deployment

The project includes Streamlit configuration and a `packages.txt` file for required Linux system libraries.

For hosted deployment:

- Install dependencies from `requirements.txt`.
- Add `GROQ_API_KEY` under the deployment's secret or environment settings if AI coaching is required.
- Configure TURN credentials when direct WebRTC connections fail behind strict network policies.
- Expect hosted SQLite storage to be ephemeral unless a persistent database or volume is configured.

## Known limitations

- Form analysis uses 2D camera landmarks and may vary with camera position.
- Only one person is tracked at a time.
- Sign-in uses a name rather than password-based authentication.
- Form thresholds are fixed and may require tuning for different users.
- Camera visibility and lighting strongly affect pose detection accuracy.
