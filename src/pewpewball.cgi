#!/usr/bin/perl
# Copyright (c) 2025 Bob Beck <beck@obtuse.com>
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

use warnings;
use strict;

use PDF::API2;
use CGI ':standard';


#######
# Helpful constants.

# PDF natively uses a point size of 72 per inch, so all coordinates are
# done based on that.
use constant mm => 25.4 / 72;
use constant inches => 1 / 72;


######
# Round a number.
sub round($$)
{
  my ($value, $places) = @_;
  my $factor = 10**$places;
  return int($value * $factor + 0.5) / $factor;
}

sub makeBallTarget($$$$$) {
    my($diameter, $units, $paper, $colour, $background) = @_;

    my @colours = ("black", "white", "red", "lime", "fuchsia", "orange", "blue", "green",
		   "navy", "yellow", "olive", "gray");

    my @papers= ("A0", "A1", "A2", "A3", "A4", "Letter", "Legal", "11x17", "12x18", "24x36", "36x48", "48x48");

    die "Paper $paper is not valid"
	unless (grep(/^$paper$/, @papers));

    die "Colour $colour is not valid"
	unless (grep(/^$colour$/, @colours));

    die "Background $background is not valid"
	unless (grep(/^$background$/, @colours));

    if ($background eq $colour) {
	$background = "white";
	$colour = "black";
    }

    die "Units $units is not valid"
	unless (($units eq "mm") |
		$units eq "inches" 
	);

    die "Diameter out of range" if ($diameter < 0 || $diameter > 200000);

    my $pdf  = PDF::API2->new;

    # Try to prevent scaling in viewers which may turn into scaling when
    # printed from viewers (i.e. a browser) instead of sending the file
    # directly to a printer.
    $pdf->preferences(-printscalingnone=>1);

    # Set our page boundaries to the correct paper size, with repeated
    # hints to attempt to ensure the randomly written browser and
    # printer software stacks that will be touching this will
    # hopefully be convinced to not pervert it themselves. We probably
    # can't win 100% of the time, but it would be nice if it is usually
    # correct in the common cases with the correct paper size selected.
    $pdf->mediabox($paper);
    my $page = $pdf  -> page;
    $page->boundaries(media => $paper);

    my $gfx  = $page -> graphics();
    my $txt  = $page -> text;

    my $radius = $diameter / 2;
    my $radius_in_points  = ($units eq  "mm") ? ($radius / mm) : ($radius / inches);

    # Compute how big in millimetres it is supposed to be. We
    # display this right on the target for confirmation purposes.
    my $diameterinmm = round($radius_in_points * mm * 2.0, 0);
    # Metric is hard in some places.
    my $diameterininches = round(($radius_in_points * inches) * 2.0, 2);

    my ($x1, $y1, $x2, $y2) = $page->boundaries('media');

    # Draw the background rectangle, if we are not "white"
    if ($background ne "white") {
	$gfx -> fillcolor($background);
	$gfx -> strokecolor($background);
	$gfx -> rectangle($x1, $y1, $x2, $y2);
	$gfx ->fill;
    }

    $txt -> fillcolor($colour);
    $txt -> strokecolor($colour);
    # Finally, put some text on the target
    $txt->font($pdf->corefont('Helvetica Bold'), 14);
    $txt->position($x1 + 30, $y2 - 30);

    
    $txt->text ("pewpewball.com");
    $txt->font($pdf->corefont('Helvetica'), 12);
    $txt->crlf();
    if ($radius_in_points * 2 > $x2 - $x1 || $radius_in_points * 2 > $y2 - $y1) {
	$txt->crlf();
	$txt->crlf();
        $txt->font($pdf->corefont('Helvetica Bold'), 18);
	$txt->text("Your Balls Are Too Big!");
	$txt->crlf();
	$txt->text("Balls that are $diameter $units wide can not print on $paper paper");
	$txt->crlf();
	$txt->text("You will need to choose a larger paper size, or smaller balls");
    } else {
	$txt->text ("Some balls are shot for charity, and some for fancy dress,");
	$txt->crlf();
	$txt->text ("But when they're shot for pleasure they're the balls that I like best.");
	$txt->font($pdf->corefont('Helvetica'), 10);
	$txt->crlf();
	$txt->text("Check that the target is $diameterinmm mm ($diameterininches inches) wide before shooting!");
	$txt->crlf();
	$txt->text("If the target has not printed correctly, check that your printer and tray settings are set to $paper");

	# Finally, let's draw big ball.
	$gfx -> fillcolor($colour);
	$gfx -> strokecolor($colour);
	# find the centre of the page.
	my $midx = ($x2 - $x1) / 2;
	my $midy = ($y2 - $y1) / 2;
	# make the circle at the centre of the page
	$gfx -> circle( $midx, $midy, $radius_in_points);
	$gfx -> fill;
    }

    return $pdf->to_string();
    $pdf -> end;
}

my $cgi = CGI->new();
my $Diameter = $cgi->param('Diameter'); 
my $Units = $cgi->param('Units'); 
my $Paper = $cgi->param('Paper');
my $Colour = $cgi->param('Colour');
my $Background = $cgi->param('Background');

my $pdfstring = makeBallTarget($Diameter, $Units, $Paper, $Colour, $Background);
print $cgi->header('application/pdf');
print $pdfstring;

