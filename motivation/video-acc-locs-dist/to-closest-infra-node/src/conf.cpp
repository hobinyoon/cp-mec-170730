#include <iostream>

#include <boost/filesystem.hpp>
#include <boost/regex.hpp>

#include "cons.h"
#include "conf.h"
#include "util.h"


using namespace std;

namespace Conf {
	namespace po = boost::program_options;
	po::variables_map _vm;

	void _ParseArgs(int argc, char* argv[]) {
		po::options_description od("Allowed options");
		od.add_options()
			("usa_map", po::value<string>()->default_value("~/work/castnet/misc/us-states-map/usa.txt"))
			("video_access_loc", po::value<string>()->default_value(
				"~/work/mec-node-placement/motivation/access-locations-most-freq-accessed-videos/gen-data/.result/acc-locs/001-Y4MnpzG5Sqc"))
			("out_dn", po::value<string>()->default_value(str(boost::format("%s/../.result") % boost::filesystem::path(__FILE__).parent_path().string())))
			("help", "show help message")
			;

		po::store(po::command_line_parser(argc, argv).options(od).run(), _vm);
		po::notify(_vm);

		if (_vm.count("help") > 0) {
			// well... this doesn't show boolean as string.
			cout << std::boolalpha;
			cout << od << "\n";
			exit(0);
		}

		// Print all parameters
		Cons::P("Options:");
		for (const auto o: _vm) {
			Cons::P(boost::format("  %s=%s") % o.first % o.second.as<string>());
		}
	}

	void Init(int argc, char* argv[]) {
		_ParseArgs(argc, argv);
	}

	const string GetFn(const string& k) {
		// Use boost::regex. C++11 regex works from 4.9. Ubuntu 14.04 has g++ 4.8.4.
		//   http://stackoverflow.com/questions/8060025/is-this-c11-regex-error-me-or-the-compiler
		return boost::regex_replace(
				_vm[k].as<string>()
				, boost::regex("~")
				, Util::HomeDir());
	}
};
