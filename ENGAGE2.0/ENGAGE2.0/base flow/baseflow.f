      program baseflow

!!    ~ ~ ~ PURPOSE ~ ~ ~
!!    this program estimates groundwater contributions from
!!    USGS streamflow records.  It uses a recursive filter 
!!    technique to seperate base flow and also calculates the 
!!    streamflow recession constant (alpha)

!!    ~ ~ ~ VARIABLES ~ ~ ~
!!    name        |units         |definition
!!    ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
!!    alf         |none          |alpha factor for groundwater recharge
!!    alpha(:)    |none          |slope of the baseflow recession
!!    amn         |m^3/s         |minimum flow in recession
!!    aveflo(:)   |m^3/s         |average flow during the computation of the
!!                               |master recession curve; these values are 
!!                               |used to fill in any ranges of flow that
!!                               |are not contained in any of the recession
!!                               |curves
!!    baseq(:,:)  |m^3/s         |base flow
!!      baseq(1,:)|m^3/s         |base flow calculated in first pass
!!      baseq(2,:)|m^3/s         |base flow calculated in second pass
!!      baseq(3,:)|m^3/s         |base flow calculated in third pass
!!    bfd         |days          |baseflow days for groundwater recharge
!!    bfdd(:)     |days          |baseflow days for a recession
!!    bflw_fr1    |none          |fraction of streamflow that is base flow 
!!                               |estimated by first pass
!!    bflw_fr2    |none          |fraction of streamflow that is base flow 
!!                               |estimated by second pass
!!    bflw_fr3    |none          |fraction of streamflow that is base flow 
!!                               |estimated by third pass
!!    date        |none          |date as a string YYYYMMDD
!!    eof         |none          |end of file flag: 
!!                               | -1 when end of file is reached
!!    eof1        |none          |end of file flag:
!!                               |  -1 when end of file is reached
!!    f1          |none          |equation coefficient
!!    f2          |none          |equation coefficient
!!    florec(:,:) |m^3/s         |flow rates during the base flow recession
!!                               |argument 1 is the day within the recession
!!                               |argument 2 is the recession number
!!    flwfile     |NA            |name of file containing USGS flow data
!!    flwfileo    |NA            |name of output file for daily baseflow values
!!    i           |none          |counter
!!    icount(:)   |none          |keeps track of where the smallest flow
!!                               |recession curve falls on the x axis (day line)
!!    idone(:)    |none          |used to identify the recession curve with the
!!                               |lowest flow value
!!    iday(:)     |none          |day in month of flow record
!!    igap        |none          |variable to skip/perform calcs for gaps in
!!                               |flow
!!    iprint      |none          |daily printout code:
!!                               |0 do not print daily values
!!                               |1 print daily values
!!    isumd       |none          |number of records processed
!!    iyr(:)      |none          |year of flow record
!!    j           |none          |counter
!!    jday(:)     |none          |julian date of flow record
!!    k           |none          |store array location value
!!    leapyr      |none          |leap year flay 
!!                               |(0 is leap year/1 isn't leap year)
!!    mon(:)      |none          |month of flow record
!!    nd          |days          |number of days in current recession analysis
!!    ndays       |none          |number of days of data in USGS flow file
!!    ndmax       |days          |maximum number of days for alpha calculation
!!    ndmin       |days          |minimum number of days for alpha calculation
!!    ndreg(:)    |days          |number of days during base flow recession
!!                               |number i
!!    now         |none          |array location in florec of the smallest flow
!!    np          |none          |number of recessions used to calculate alpha
!!                               |and y intercept
!!    npr         |none          |total number of base flow recessions 
!!                               |(all the recessions are combined to compute
!!                               |the master recession curve)
!!    npreg(:)    |none          |number of points on the master recession
!!                               |curve
!!    nregmx      |none          |number of baseflow recessions per year that
!!                               |are used in the master recession curve
!!                               |regression
!!    qaveln(:)   |m^3/s         |Log(average flow) for a recession
!!    q0(:)       |m^3/s         |flow at start of the base flow recession
!!    q10(:)      |m^3/s         |flow at the end of the base flow recession
!!    sflow       |m^3/s         |USGS streamflow value for record
!!    slope       |none          |slope of baseflow recession curve
!!    ssxx        |none          |intermediate calc.
!!    ssxy        |none          |intermediate calc.
!!    strflow(:)  |m^3/s         |USGS streamflow value for record
!!    sumbf1      |m^3/s         |sum of baseflow values calculated by pass 1
!!                               |for entire period of record
!!    sumbf2      |m^3/s         |sum of baseflow values calculated by pass 2
!!                               |for entire period of record
!!    sumbf3      |m^3/s         |sum of baseflow values calculated by pass 3
!!                               |for entire period of record
!!    sumstrf     |m^3/s         |sum of streamflow values for period of record
!!    sumx        |none          |intermediate calc.
!!    sumx2       |none          |intermediate calc.
!!    sumxy       |none          |intermediate calc.
!!    sumy        |none          |intermediate calc.
!!    surfq(:)    |m^3/s         |streamflow from surface runoff
!!    titldum     |NA            |variable used to process unimportant lines
!!    x           |none          |icount value expressed as real number
!!    yint        |none          |y intercept for baseflow regression curve
!!    ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

!!    ~ ~ ~ ~ ~ ~ END SPECIFICATIONS ~ ~ ~ ~ ~ ~

      character (len=15) :: flwfile, titldum, flwfileo
      integer :: eof, ndays, isumd, date, leapyr, i, eof1, ndmin, ndmax
      integer :: iprint
      real :: sflow, f1, f2, bflw_fr1, bflw_fr2, bflw_fr3
      real :: sumbf1, sumbf2, sumbf3, sumstrf
      integer, dimension (:), allocatable :: mon, iday, jday, iyr
      real, dimension (:), allocatable :: strflow, surfq
      real, dimension (:,:), allocatable :: baseq

      integer, parameter :: nregmx = 300
      real, dimension (:), allocatable :: alpha, q0, q10
      integer, dimension (:), allocatable :: ndreg
      real :: ssxx, ssxy, sumx, sumy, sumxy, sumx2, alf, bfd, x, slope
      real :: yint, amn
      integer :: nd, npr, np, j, k, now, igap
      real, dimension (nregmx,200) :: florec
      real, dimension (nregmx) :: aveflo, bfdd, qaveln
      integer, dimension (200) :: icount
      integer, dimension (nregmx) :: npreg, idone

!! initialize universal variables
      ndmin = 0
      ndmax = 0
      iprint = 0
      
!! open output files
      open (3,file="baseflow.dat")
      write (3, 5000)
      write (3, 5001)
!! process input file
      eof1 = 0
      open (1,file="file.lst")
!! process preliminary information
      read (1,1000) titldum
      read (1,*) ndmin
      read (1,*) ndmax
      read (1,*) iprint
      read (1,1000) titldum
      read (1,1000) titldum


!! process USGS data files
      do
        read (1,1000,iostat=eof1) flwfile, flwfileo
        if (eof1 < 0) exit

        call caps(flwfile)
        open (2,file=flwfile)

        !! find out number of years of stream gage data
        eof = 0
        ndays = 0
        do
          read (2,*, iostat=eof) titldum
          if (eof < 0) exit
          ndays = ndays + 1
        end do
        rewind (2)

        if (ndays < 2) stop    !!if no data in file, stop program

        !! allocate arrays
        allocate (mon(ndays))
        allocate (iday(ndays))
        allocate (jday(ndays))
        allocate (iyr(ndays))
        allocate (strflow(ndays))
        allocate (surfq(ndays))
        allocate (baseq(3,ndays))

        !! initialize arrays
        mon = 0
        iday = 0
        jday = 0
        iyr = 0
        strflow = 0.
        surfq = 0.
        baseq = 0.
     
        !! read in streamflow data
        eof = 0
        read (2,*) titldum
        isumd = 1
        do
          read (2,*, iostat=eof) date, sflow
	if (sflow > 9998.) sflow = 0.0
          if (eof < 0) exit
          iyr(isumd) = date / 10000
          date = date - (iyr(isumd) * 10000)
          mon(isumd) = date / 100
          iday(isumd) = date - (mon(isumd) * 100)
          leapyr = 0
          if (Modulo (iyr(isumd), 4) /= 0) leapyr = 1
          select case (mon(isumd))
            case (1)
              jday(isumd) = iday(isumd)
            case (2)
              jday(isumd) = 31 + iday(isumd)
            case (3)
              jday(isumd) = 60 + iday(isumd) - leapyr
            case (4)
              jday(isumd) = 91 + iday(isumd) - leapyr
            case (5)
              jday(isumd) = 121 + iday(isumd) - leapyr
            case (6)
              jday(isumd) = 152 + iday(isumd) - leapyr
            case (7)
              jday(isumd) = 182 + iday(isumd) - leapyr
            case (8)
              jday(isumd) = 213 + iday(isumd) - leapyr
            case (9)
              jday(isumd) = 244 + iday(isumd) - leapyr
            case (10)
              jday(isumd) = 274 + iday(isumd) - leapyr
            case (11)
              jday(isumd) = 305 + iday(isumd) - leapyr
            case (12)
              jday(isumd) = 335 + iday(isumd) - leapyr
          end select
          strflow(isumd) = sflow
          isumd = isumd + 1
        end do
        close (2)

        !! perform passes to calculate base flow
        f1 = 0.925
        f2 = 0.
        f2 = (1. + f1) / 2.
        surfq(1) = strflow(1) * .5
        baseq(1,1) = strflow(1) - surfq(1)
        baseq(2,1) = baseq(1,1)
        baseq(3,1) = baseq(1,1)

        !! make the first pass (forward)    
        do i = 2, isumd
          surfq(i) = f1 * surfq(i-1) + f2 * (strflow(i) - strflow(i-1))
          if (surfq(i) < 0.) surfq(i) = 0.
          baseq(1,i) = strflow(i) - surfq(i)
          if (baseq(1,i) < 0.) baseq(1,i) = 0.
          if (baseq(1,i) > strflow(i)) baseq(1,i) = strflow(i)
        end do

        !! make the second pass (backward)     
        baseq(2,isumd - 1) = baseq(1,isumd - 1)
        do i = isumd - 2, 1, -1
          surfq(i) = f1 * surfq(i+1) + f2 * (baseq(1,i) - baseq(1,i+1))
          if (surfq(i) < 0.) surfq(i) = 0.
          baseq(2,i) = baseq(1,i) - surfq(i)
          if (baseq(2,i) < 0.) baseq(2,i) = 0.
          if (baseq(2,i) > baseq(1,i)) baseq(2,i) = baseq(1,i)
        end do

        !! make the third pass (forward)    
        baseq(3,isumd - 1) = baseq(1, isumd - 1)
        do i = 2, isumd
          surfq(i) = f1 * surfq(i-1) + f2 * (baseq(2,i)- baseq(2,i-1))
          if (surfq(i) < 0.) surfq(i) = 0.
          baseq(3,i) = baseq(2,i) - surfq(i)
          if (baseq(3,i) < 0.) baseq(3,i) = 0.
          if (baseq(3,i) > baseq(2,i)) baseq(3,i) = baseq(2,i)
        end do

        !! perform summary calculations
        sumbf1 = 0.
        sumbf2 = 0.
        sumbf3 = 0.
        sumstrf = 0.
        sumstrf = Sum(strflow)
        do i = 1, isumd
          sumbf1 = sumbf1 + baseq(1,i)
          sumbf2 = sumbf2 + baseq(2,i)
          sumbf3 = sumbf3 + baseq(3,i)
        end do

        !! calculate baseflow fractions
        bflw_fr1 = 0.
        bflw_fr2 = 0.
        bflw_fr3 = 0.
        bflw_fr1 = sumbf1 / sumstrf
        bflw_fr2 = sumbf2 / sumstrf
        bflw_fr3 = sumbf3 / sumstrf



        !! compute streamflow recession constant (alpha)

        !! allocate arrays
        allocate (alpha(ndays))
        allocate (ndreg(ndays))
        allocate (q0(ndays))
        allocate (q10(ndays))

        !!initialize variables
        alpha = 0.
        ndreg = 0
        aveflo = 0.
        florec = 0.
        npreg = 0
        idone = 0
        bfdd = 0.
        qaveln = 0.
        q0 = 0.
        q10 = 0.

        nd = 0
        do i = 1, ndays - 1
          if (strflow(i) <= 0.) then
            nd = 0
          else
            if (baseq(1,i) / strflow(i) < 0.99) then
              if (nd >= ndmin) then
                alpha(i) = Log(strflow(i-nd) / strflow(i-1)) / nd
                ndreg(i) = nd
!               write (3,6003) i, mon(i), iyr(i), nd, strflow(i-nd),    &
!    &              strflow(i-1), alpha(i)
              endif
              nd = 0
            else
              nd = nd + 1
              if (nd >= ndmax) then
                alpha(i) = Log(strflow(i-nd+1) / strflow(i)) / nd
                ndreg(i) = nd
!               write (3,6003) i, mon(i), iyr(i), nd, strflow(i-nd+1),  &
!    &              strflow(i), alpha(i)
                nd = 0
              endif
            endif
          endif
        end do

        npr = 0.
        do i = 1, ndays
          !! compute x and y coords for alpha regression analysis
          if (alpha(i) > 0.) then
            if (mon(i) <= 2 .or. mon(i) >= 11) then
              npr = npr + 1
              q10(npr) = strflow(i-1)
              q0(npr) = strflow(i-ndreg(i))
              if (q0(npr) - q10(npr) > 0.001) then
                bfdd(npr) = ndreg(i) / (Log(q0(npr)) - Log(q10(npr)))
                qaveln(npr) = Log((q0(npr) + q10(npr)) / 2.)
                kk = 0
                do k = 1, ndreg(i)
                  x = 0.
                  x = Log(strflow(i-k))
                  if (x > 0.) then
                    kk = kk + 1
                    florec(kk,npr) = x
                  end if
                end do
                if (kk == 0) npr = npr - 1
              end if
            end if
          end if
        end do

        !! estimate master recession curve
        if (npr > 1) then

          np = 0
          sumx = 0.
          sumy = 0.
          sumxy = 0.
          sumx2 = 0.
          do i = 1, npr
            np = np + 1
            x = qaveln(i)
            sumx = sumx + x
            sumy = sumy + bfdd(i)
            sumxy = sumxy + x * bfdd(i)
            sumx2 = sumx2 + x * x
          end do
          ssxy = 0.
          ssxx = 0.
          slope = 0.
          yint = 0.
          ssxy = sumxy - (sumx * sumy) / np
          ssxx = sumx2 - (sumx * sumx) / np
          slope = ssxy / ssxx
          yint = sumy / np - slope * sumx / np

          !! find the recession curve with the lowest point on it
          do j = 1, npr
            amn = 1.e20
            do i = 1, npr
              if (idone(i) == 0) then
                if (florec(1,i) < amn) then
                  amn = 0.
                  now = 0
                  amn = florec(1,i)
                  now = i
                end if
              end if
            end do
            idone(now) = 1

            !! now is the number in array florec of the current smallest flow
            !! icount keeps track of where the now recession curve falls on the
            !! x axis (day line)

            igap = 0
            if (j == 1) then
              icount(now) = 1
              igap = 1
            else
              do i = 1, nregmx
                if (florec(1,now) <= aveflo(i)) then
                  icount(now) = i
                  igap = 1
                  exit
                end if
              end do
            end if

            !! if there is a gap, run linear regression on the average flow
            if (igap == 0) then
              np = 0
              sumx = 0.
              sumy = 0.
              sumxy = 0.
              sumx2 = 0.
              do i = 1, nregmx
                if (aveflo(i) > 0.) then
                  np = np + 1
                  x = 0.
                  x = Real(i)
                  sumx = sumx + x
                  sumy = sumy + aveflo(i)
                  sumxy = sumxy + x * aveflo(i)
                  sumx2 = sumx2 + x * x
                end if
              end do
              ssxy = 0.
              ssxx = 0.
              slope = 0.
              yint = 0.
              if (sumx > 1.) then
                ssxy = sumxy - (sumx * sumy) / np
                ssxx = sumx2 - (sumx * sumx) / np
                slope = ssxy / ssxx
                yint = sumy / np - slope * sumx / np
                icount(now) = (florec(1,now) - yint) / slope
              else
                slope = 0.
                yint = 0.
                icount(now) = 0.
              end if
            end if

            !! update average flow array
            do i = 1, ndmax
              if (florec(i,now) > 0.0001) then
                k = 0
                k = icount(now) + i - 1
                aveflo(k) = (aveflo(k) * npreg(k) + florec(i,now))      &
     &                                                  / (npreg(k) + 1)
                if (aveflo(k) <= 0.) aveflo(k) = slope * i + yint
                npreg(k) = npreg(k) + 1
              else
                exit
              end if
            end do
          end do

          !! run alpha regression on all adjusted points
          !! calculate alpha factor for groundwater
          np = 0
          sumx = 0.  
          sumy = 0.
          sumxy = 0.
          sumx2 = 0.
          do j = 1, npr
            do i = 1, ndmax
              if (florec(i,j) > 0.) then
                np = np + 1
                x = 0
                x = Real(icount(j)+i)
                sumx = sumx + x
                sumy = sumy + florec(i,j)
                sumxy = sumxy + x * florec(i,j)
                sumx2 = sumx2 + x * x
              else
                exit
              end if
            end do
          end do
          ssxx = 0.
          ssxy = 0.
          alf = 0.
          bfd = 0.
          ssxy = sumxy - (sumx * sumy) / np
          ssxx = sumx2 - (sumx * sumx) / np
          alf = ssxy / ssxx
          bfd = 2.3 / alf

          write(3,5002) flwfile, bflw_fr1, bflw_fr2, bflw_fr3, npr, alf,&
     &                  bfd
        else
          write(3,5002) flwfile, bflw_fr1, bflw_fr2, bflw_fr3
        end if

        !! if daily baseflow values are wanted
        if (iprint == 1) then
          call caps(flwfileo)
          open (4,file = flwfileo)
          write (4,6000) flwfile
          write (4,6001)
          do i = 1, ndays
            write(4,6002) iyr(i), mon(i), iday(i), strflow(i),          &
     &                    baseq(1,i), baseq(2,i), baseq(3,i)
          end do
          close (4)
        end if
      
        !! deallocate arrays
        deallocate (mon)
        deallocate (iday)
        deallocate (jday)
        deallocate (iyr)
        deallocate (strflow)
        deallocate (surfq)
        deallocate (baseq)
        deallocate (alpha)
        deallocate (ndreg)
        deallocate (q0)
        deallocate (q10)

      end do

 1000 format(a15,1x,a15)
 2000 format(i4,4f12.2)
 5000 format("Baseflow data file: this file summarizes the fraction ",  &
     &       "of streamflow that is contributed by baseflow for each ", &
     &       "of the 3 passes made by the program")
 5001 format (/,"Gage file      ",1x,"Baseflow Fr1",1x,"Baseflow Fr2",  &
     &        1x,"Baseflow Fr3",1x,"   NPR",1x,"Alpha Factor",1x,       &
     &        "Baseflow Days")
 5002 format(a15,1x,f12.2,1x,f12.2,1x,f12.2,1x,i6,1x,f12.4,1x,f13.4)
 6000 format ("Daily baseflow filters values for data from: ",a15)
 6001 format ("YEARMNDY",1x,"  Streamflow",1x," Bflow Pass1",1x,        &
     &        " Bflow Pass2",1x," Bflow Pass3")
 6002 format (i4,i2,i2,1x,e12.6,1x,e12.6,1x,e12.6,1x,e12.6)
 6003 format (4i6,3f10.4)
      stop
      end

