/// @file

#include <iostream>
#include <fstream>
#include <string.h>
#include <errno.h>

#include "wavfile_mono.h"
#include "pitch_analyzer.h"

#include "docopt.h"

#define FRAME_LEN   0.030 /* 30 ms. */
#define FRAME_SHIFT 0.015 /* 15 ms. */

using namespace std;
using namespace upc;

static const char USAGE[] = R"(
get_pitch - Pitch Estimator 

Usage:
    get_pitch [options] <input-wav> <output-txt>
    get_pitch (-h | --help)
    get_pitch --version

Options:
    - p, --pot FLOAT  llindar de potència per la decisió sonor/sord [Default: 0]
    - 1, --r1norm FLOAT  llindar de la correlació de 1 per la decisió sonor/sord [Default: 0.6]
    -M, --rmaxnorm FLOAT  llindar de correlació al max secundari per la decisió sonor/sord [Default: 0.6]

    -h, --help  Show this screen
    --version   Show the version of the project

Arguments:
    input-wav   Wave file with the audio signal
    output-txt  Output file: ASCII file with the result of the estimation:
                    - One line per frame with the estimated f0
                    - If considered unvoiced, f0 must be set to f0 = 0
)";

int main(int argc, const char *argv[]) {
	/// \DONE 
	///  Modify the program syntax and the call to **docopt()** in order to
	///  add options and arguments to the program.
    std::map<std::string, docopt::value> args = docopt::docopt(USAGE,
        {argv + 1, argv + argc},	// array of arguments, without the program name
        true,    // show help if requested
        "2.0");  // version string

	std::string input_wav = args["<input-wav>"].asString();
	std::string output_txt = args["<output-txt>"].asString();
  float llindar_pot = stof(args["--pot"].asString());
  float llindar_r1norm = stof(args["--r1norm"].asString());
  float llindar_rmaxnorm = stof(args["--rmaxnorm"].asString());

  // Read input sound file
  unsigned int rate;
  vector<float> x;
  if (readwav_mono(input_wav, rate, x) != 0) {
    cerr << "Error reading input file " << input_wav << " (" << strerror(errno) << ")\n";
    return -2;
  }

  int n_len = rate * FRAME_LEN;
  int n_shift = rate * FRAME_SHIFT;

  // Define analyzer
  PitchAnalyzer analyzer(n_len, rate, PitchAnalyzer::RECT, 50, 500, llindar_pot, llindar_r1norm, llindar_rmaxnorm);

  /// \DONE
  /// Preprocess the input signal in order to ease pitch estimation. For instance,
  /// central-clipping or low pass filtering may be used.
  
  // 1. Filtrado paso bajo (Low-pass filter)
  for (unsigned int i = 1; i < x.size(); ++i) {
    x[i] = 0.5f * x[i] + 0.5f * x[i-1];
  }

  // 2. Center clipping
  float max_val = 0.0f;
  for (unsigned int i = 0; i < x.size(); ++i) {
    float val = x[i] > 0 ? x[i] : -x[i];
    if (val > max_val) max_val = val;
  }
  float cl_threshold = max_val * 0.3f;
  for (unsigned int i = 0; i < x.size(); ++i) {
    float val = x[i] > 0 ? x[i] : -x[i];
    if (val < cl_threshold) {
      x[i] = 0.0f;
    } else if (x[i] > 0) {
      x[i] -= cl_threshold;
    } else {
      x[i] += cl_threshold;
    }
  }

  // Iterate for each frame and save values in f0 vector
  vector<float>::iterator iX;
  vector<float> f0;
  for (iX = x.begin(); iX + n_len < x.end(); iX = iX + n_shift) {
    float f = analyzer(iX, iX + n_len);
    f0.push_back(f);
  }

  /// \DONE
  /// Postprocess the estimation in order to supress errors. For instance, a median filter
  /// or time-warping may be used.
  
  if (f0.size() > 2) {
    vector<float> f0_f = f0;
    for (unsigned int i = 1; i < f0.size() - 1; ++i) {
      float a = f0[i-1], b = f0[i], c = f0[i+1];
      if ((a <= b && b <= c) || (c <= b && b <= a)) f0_f[i] = b;
      else if ((b <= a && a <= c) || (c <= a && a <= b)) f0_f[i] = a;
      else f0_f[i] = c;
    }
    f0 = f0_f;
  }

  // Write f0 contour into the output file
  ofstream os(output_txt);
  if (!os.good()) {
    cerr << "Error reading output file " << output_txt << " (" << strerror(errno) << ")\n";
    return -3;
  }

  os << 0 << '\n'; //pitch at t=0
  for (iX = f0.begin(); iX != f0.end(); ++iX) 
    os << *iX << '\n';
  os << 0 << '\n';//pitch at t=Dur

  return 0;
}
