#include <signal.h>
#include <unistd.h>
#include <iostream>
#include <boost/filesystem.hpp>

#include "conf.h"
#include "cons.h"
#include "util.h"
#include "youtube-data.h"


using namespace std;

void on_signal(int sig) {
	cout << boost::format("\nGot a signal: %d\n%s\n") % sig % Util::Indent(Util::StackTrace(1), 2);
  exit(1);
}

int main(int argc, char* argv[]) {
	try {
		signal(SIGSEGV, on_signal);
		signal(SIGINT, on_signal);

		Conf::Init(argc, argv);

		const string dn = boost::filesystem::path(Conf::GetFn("out_file")).parent_path().string();
		boost::filesystem::create_directories(dn);

		YoutubeData::Load();
		YoutubeData::GenNumAccessesByVideos();
		YoutubeData::FreeMem();
	} catch (const exception& e) {
		cerr << "Got an exception: " << e.what() << "\n";
		return 1;
	}
	return 0;
}
